PadelVision Binary Movement Dataset v0.2

Files:
1. binary_point_reference.csv
   - Expected binary movement for all 33 MediaPipe pose landmarks.
   - Organized by stroke and movement phase.

2. video_binary_matrix_example_forehand.csv
   - 140-frame example.
   - Each frame contains all 33 body points.
   - Expected binary movement is already placed directly in the video matrix.
   - Fill Player_X/Y/Z from pose estimation, compute dX/dY/dZ, then calculate observed binary bits.

3. video_binary_matrix_blank_template.csv
   - Blank 120-frame template for future videos.

4. binary_encoding.csv
   - Definition of the six binary movement bits.

Binary order: [X_Pos, X_Neg, Y_Pos, Y_Neg, Z_Pos, Z_Neg]
Example: F+R = 101000
Stable = 000000

Important: coordinates must be transformed into a player-centered coordinate system before comparison.
Current technical targets are a prototype and still require validation by expert padel coaches.
