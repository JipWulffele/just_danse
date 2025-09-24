import numpy as np
import mediapipe as mp

class DanceJudge:
    def __init__(self, ref_keypoints_seq, shifts=[0, 10, 16, 18], angle_deg=90, frame_for_scale=3):
        """
        ref_keypoints_seq: numpy array [num_frames, 33, 3] with reference keypoints
        shifts: list of backward shifts to test
        angle_deg: rotation angle for user keypoints
        frame_for_scale: reference frame index used to compute scaling
        """
        self.ref_keypoints_seq = ref_keypoints_seq
        self.shifts = shifts
        self.angle_deg = angle_deg
        self.frame_for_scale = frame_for_scale

        # Accumulators for each shift
        self.sums = {s: 0.0 for s in shifts}
        self.counts = {s: 0 for s in shifts}

        # State
        self.frame_idx = 0
        self.best_shift = None
        self.score = None
        self.scale_x_u = None
        self.scale_x_r = None
        self.scale_y = None
        self.scaling_computed = False

    def rotate_keypoints(self, keypoints):
        """Rotate 2D keypoints around the origin (0,0) by a given angle in degrees."""
        angle_rad = np.deg2rad(self.angle_deg)
        R = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad),  np.cos(angle_rad)]
        ])
        kp = keypoints.copy()
        if kp.shape[1] >= 2:
            xy = kp[:, :2].T
            rotated_xy = R @ xy
            kp[:, :2] = rotated_xy.T
        return kp

    def normalize_keypoints(self, keypoints):
        """Shift hip midpoint to (0,0). No scaling here (scales applied separately)."""
        keypoints = keypoints.copy()
        left_hip = keypoints[mp.solutions.pose.PoseLandmark.LEFT_HIP.value][:2]
        right_hip = keypoints[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value][:2]
        hip_center = (left_hip + right_hip) / 2
        keypoints[:, 0:2] -= hip_center
        return keypoints

    def compute_scaling(self, user_kp_first):
        """Compute scaling factors using user first frame + ref frame_for_scale."""
        mp_pose = mp.solutions.pose

        # Rotate + normalize
        user_kp = self.rotate_keypoints(user_kp_first)
        ref_kp = self.ref_keypoints_seq[self.frame_for_scale]
        user_kp = self.normalize_keypoints(user_kp)
        ref_kp = self.normalize_keypoints(ref_kp)

        # --- X-axis scaling (nose-hip distance) ---
        nose_u = user_kp[mp_pose.PoseLandmark.NOSE.value][:2]
        nose_r = ref_kp[mp_pose.PoseLandmark.NOSE.value][:2]
        hip_center_u = (user_kp[mp_pose.PoseLandmark.LEFT_HIP.value][:2] +
                        user_kp[mp_pose.PoseLandmark.RIGHT_HIP.value][:2]) / 2
        hip_center_r = (ref_kp[mp_pose.PoseLandmark.LEFT_HIP.value][:2] +
                        ref_kp[mp_pose.PoseLandmark.RIGHT_HIP.value][:2]) / 2

        self.scale_x_u = 1.0 / (nose_u[0] - hip_center_u[0])
        self.scale_x_r = 1.0 / (nose_r[0] - hip_center_r[0])

        # --- Y-axis scaling (hip width) ---
        hip_dist_u = np.linalg.norm(user_kp[mp_pose.PoseLandmark.LEFT_HIP.value][:2] -
                                    user_kp[mp_pose.PoseLandmark.RIGHT_HIP.value][:2])
        hip_dist_r = np.linalg.norm(ref_kp[mp_pose.PoseLandmark.LEFT_HIP.value][:2] -
                                    ref_kp[mp_pose.PoseLandmark.RIGHT_HIP.value][:2])
        self.scale_y = hip_dist_r / hip_dist_u

        self.scaling_computed = True
        print(f"Scale X (user): {self.scale_x_u:.3f}, Scale X (ref): {self.scale_x_r:.3f}, Scale Y: {self.scale_y:.3f}")

    def update(self, user_landmarks, expected_idx, method="mean"):
        """
        Update judge state with new user landmarks.
        Scaling is computed once from the first user frame.
        x scaling could be computed each frame but we keep it fixed.
        y scaling must be computed at the beginning and kept fixed to avoid instability do to movements of the body.

        user_landmarks: mediapipe landmarks for current frame
        expected_idx: reference frame index
        Returns: (score, best_shift)
        """
        # Convert to numpy
        user_kp = np.array([[lm.x, lm.y, lm.z] for lm in user_landmarks])

        # Compute scaling factors once (first user frame)
        if not self.scaling_computed:
            self.compute_scaling(user_kp)

        # Rotate + normalize
        user_kp = self.rotate_keypoints(user_kp)
        user_kp = self.normalize_keypoints(user_kp)

        # Apply scaling
        user_kp[:, 0] *= self.scale_x_u
        user_kp[:, 1] *= self.scale_y

        # Exclude indices
        exclude_idx = list(range(1, 11)) + [21, 22, 23, 24, 29, 30]
        mask = np.array([i for i in range(user_kp.shape[0]) if i not in exclude_idx])

        # Update distances
        for shift in self.shifts:
            if expected_idx - shift < 0 or expected_idx >= len(self.ref_keypoints_seq):
                continue

            ref_kp = self.ref_keypoints_seq[expected_idx - shift]
            ref_kp = self.normalize_keypoints(ref_kp)
            ref_kp[:, 0] *= self.scale_x_r  # only X-axis scaling for ref

            if ref_kp is not None and not np.isnan(ref_kp).any():
                user_sel = user_kp[mask]
                ref_sel = ref_kp[mask]
                dist = np.nanmean(np.linalg.norm(user_sel - ref_sel, axis=1))
                self.sums[shift] += dist
                self.counts[shift] += 1

        # Compute best score so far
        valid_shifts = {s: self.sums[s] / self.counts[s] for s in self.shifts if self.counts[s] > 0}
        if valid_shifts:
            self.best_shift = min(valid_shifts, key=valid_shifts.get)
            self.score = valid_shifts[self.best_shift]
        else:
            self.best_shift, self.score = None, None

        self.frame_idx = expected_idx
        return self.score, self.best_shift
