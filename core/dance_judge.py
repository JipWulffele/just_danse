import numpy as np
import mediapipe as mp

class DanceJudge:
    def __init__(self, ref_keypoints_seq, shifts=[0,10,16,18]):
        """
        ref_keypoints_seq: numpy array [num_frames, 33, 3] with reference keypoints
        normalize_fn: function to normalize user keypoints
        shifts: list of backward shifts to test
        """
        self.ref_keypoints_seq = ref_keypoints_seq
        self.shifts = shifts

        # Accumulators for each shift
        self.sums = {s: 0.0 for s in shifts}
        self.counts = {s: 0 for s in shifts}

        self.frame_idx = 0
        self.best_shift = None
        self.score = None

    def rotate_keypoints(self, keypoints, angle_deg):
        """
        Rotate 2D keypoints around the origin (0,0) by a given angle in degrees.
        Keeps z unchanged.

        Parameters:
            keypoints: numpy array [num_points, 3] or [num_points, 2]
            angle_deg: angle in degrees (positive = counter-clockwise)

        Returns:
            rotated_keypoints: same shape as input
        """
        angle_rad = np.deg2rad(angle_deg)

        # Rotation matrix
        R = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad),  np.cos(angle_rad)]
        ])

        kp = keypoints.copy()

        # If (x,y,z), rotate only x,y
        if kp.shape[1] >= 2:
            xy = kp[:, :2].T  # shape (2, N)
            rotated_xy = R @ xy
            kp[:, :2] = rotated_xy.T

        return kp

    def normalize_keypoints(self, keypoints):
        """
        Centers the hip midpoint at (0,0) and scales so distance hip->nose = 1
        """
        keypoints = keypoints.copy()
        
        # Hip center
        left_hip = keypoints[mp.solutions.pose.PoseLandmark.LEFT_HIP.value][:2]
        right_hip = keypoints[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value][:2]
        hip_center = (left_hip + right_hip) / 2
        
        # Translate keypoints
        keypoints[:, 0:2] -= hip_center
        
        # Scale by distance hip -> nose
        nose = keypoints[mp.solutions.pose.PoseLandmark.NOSE.value][:2]
        scale = np.linalg.norm(nose)
        if scale > 0:
            keypoints[:, 0:2] /= scale
        
        return keypoints

    def update(self, user_landmarks, angle, method="mean"):
        """
        Update judge state with new user landmarks.

        user_landmarks: mediapipe landmarks for current frame
        method: distance metric, currently "mean" of Euclidean

        Returns:
            score: best mean distance up to this frame
            best_shift: shift index with best score
        """
        # Convert to numpy and normalize
        user_kp = np.array([[lm.x, lm.y, lm.z] for lm in user_landmarks])
        user_kp = self.normalize_keypoints(user_kp)
        user_kp = self.rotate_keypoints(user_kp, angle)

        # Indices to exclude
        exclude_idx = list(range(1, 11)) + [19, 20, 21, 22, 29, 30]

        # Create a mask to keep only valid points
        mask = np.array([i for i in range(user_kp.shape[0]) if i not in exclude_idx])

        # Update distances for each shift
        for shift in self.shifts:
            if self.frame_idx - shift < 0:
                continue
            if self.frame_idx >= len(self.ref_keypoints_seq):
                continue

            ref_kp = self.ref_keypoints_seq[self.frame_idx - shift]

            if ref_kp is not None and not np.isnan(ref_kp).any():
                # Filter both user and reference by the mask
                user_sel = user_kp[mask]
                ref_sel = ref_kp[mask]

                dist = np.nanmean(np.linalg.norm(user_sel - ref_sel, axis=1))
                self.sums[shift] += dist
                self.counts[shift] += 1

        # Compute provisional best score
        valid_shifts = {s: self.sums[s]/self.counts[s] for s in self.shifts if self.counts[s] > 0}
        if valid_shifts:
            self.best_shift = min(valid_shifts, key=valid_shifts.get)
            self.score = valid_shifts[self.best_shift]
        else:
            self.best_shift = None
            self.score = None

        self.frame_idx += 1
        return self.score, self.best_shift