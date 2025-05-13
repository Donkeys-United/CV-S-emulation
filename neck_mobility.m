% MATLAB script for measuring head tilt angles from video frames
clear all; close all;

% Load the video file - prompt user to select the file
[videoFileName, videoPath] = uigetfile({'*.mp4;*.avi;*.mov', 'Video Files (*.mp4,*.avi,*.mov)'}, 'Select a video file');
if videoFileName == 0
    error('No video file selected');
end
fullVideoPath = fullfile(videoPath, videoFileName);
videoObj = VideoReader(fullVideoPath);

% Get base filename (without extension) for output
[~, baseFileName, ~] = fileparts(videoFileName);

% Create arrays to store the two selected frames
selectedFrames = cell(1,2);
selectedFrameNumbers = zeros(1,2);
frameCount = 0;

% Create frame selection interface
fig = figure('Name', 'Video Frame Selector');

% Store currentFrame in the figure's UserData
currentFrame = 1;
set(fig, 'UserData', currentFrame);

% Display initial frame
frame = read(videoObj, currentFrame);
imHandle = imshow(frame);
title(sprintf('Frame %d / %d - Press → to advance, ← to go back, Space to select (2 max)', ...
    currentFrame, videoObj.NumFrames));

% Set up keyboard input handler
set(fig, 'KeyPressFcn', @(src, event)keyPressed(src, event, videoObj, imHandle));

% Wait for frame selection to complete
uiwait(fig);

% Get selected frames from base workspace (where they were saved)
img1 = selectedFrame1;
img2 = selectedFrame2;
frameNum1 = selectedFrameNumbers(1);
frameNum2 = selectedFrameNumbers(2);

% Process first image
figure('Name', 'Position 1');
imshow(img1);
title('Position 1: Select points for head tilt angle measurement');

% Instructions for point selection
annotation('textbox', [0.15, 0.01, 0.7, 0.08], 'String', ...
    'Select: 1) Ear tragus, 2) Facial reference point (eye/nose)', ...
    'FitBoxToText', 'on', 'BackgroundColor', 'white');

disp('For Position 1:');
disp('1. Click on the tragus of the ear (where the ear connects to the head)');
disp('2. Click on a consistent facial feature (bridge of nose or center of eye)');
disp('Then press Enter');

% Get 3 points (just first and third now)
disp('Select: 1) Ear tragus, 2) Facial reference point');
[x1, y1] = ginput(2); 

% Create horizontal reference point automatically
x1 = [x1(1); 0; x1(2)]; % Insert new point at index 2
y1 = [y1(1); y1(1); y1(2)];      % Insert y value (same as point 1)

% Continue with your existing drawing code
hold on;
plot(x1(1), y1(1), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Ear tragus
plot(x1(2), y1(2), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Horizontal point
plot(x1(3), y1(3), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Facial landmark

% Draw horizontal reference line in blue
line([x1(1) x1(2)], [y1(1) y1(2)], 'Color', 'b', 'LineWidth', 2);

% Draw head orientation line in red
line([x1(1) x1(3)], [y1(1) y1(3)], 'Color', 'r', 'LineWidth', 2);

% Calculate angle for first position
v1_1 = [x1(2)-x1(1), y1(2)-y1(1)]; % Horizontal vector
v1_2 = [x1(3)-x1(1), y1(3)-y1(1)]; % Head orientation vector

% Normalize vectors
v1_1 = v1_1 / norm(v1_1);
v1_2 = v1_2 / norm(v1_2);

% Calculate angle using dot product
dot_product1 = dot(v1_1, v1_2);
angle1 = acosd(dot_product1);

% Determine if angle is above or below horizontal
% If y-coordinate of point 3 is less than point 1, angle is upward
if y1(3) < y1(1)
    angle_direction1 = 'upward';
else
    angle_direction1 = 'downward';
    % Keep angle positive for consistency
end

% Display angle on first image
text(x1(1)+10, y1(1)-20, [num2str(angle1, '%.1f') '°'], 'Color', 'green', 'FontSize', 14, 'FontWeight', 'bold');
hold off;

% Process second image
figure('Name', 'Position 2');
imshow(img2);
title('Position 2: Select points for head tilt angle measurement');

% Instructions for point selection
annotation('textbox', [0.15, 0.01, 0.7, 0.08], 'String', ...
    'Select: 1) Ear tragus, 2) Same facial reference as in Position 1', ...
    'FitBoxToText', 'on', 'BackgroundColor', 'white');

disp('For Position 2:');
disp('1. Click on the tragus of the ear (where the ear connects to the head)');
disp('2. Click on the SAME facial feature as in Position 1');
disp('Then press Enter');

% Get 3 points (just first and third now)
disp('Select: 1) Ear tragus, 2) Facial reference point');
[x2, y2] = ginput(2); 

% Create horizontal reference point automatically
x2 = [x2(1); 0; x2(2)]; % Insert new point at index 2
y2 = [y2(1); y2(1); y2(2)];      % Insert y value (same as point 1)

% Continue with your existing drawing code
hold on;
plot(x2(1), y2(1), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Ear tragus
plot(x2(2), y2(2), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Horizontal point
plot(x2(3), y2(3), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Facial landmark


% Draw horizontal reference line in blue
line([x2(1) x2(2)], [y2(1) y2(2)], 'Color', 'b', 'LineWidth', 2);

% Draw head orientation line in red
line([x2(1) x2(3)], [y2(1) y2(3)], 'Color', 'r', 'LineWidth', 2);

% Calculate angle for second position
v2_1 = [x2(2)-x2(1), y2(2)-y2(1)]; % Horizontal vector
v2_2 = [x2(3)-x2(1), y2(3)-y2(1)]; % Head orientation vector

% Normalize vectors
v2_1 = v2_1 / norm(v2_1);
v2_2 = v2_2 / norm(v2_2);

% Calculate angle using dot product
dot_product2 = dot(v2_1, v2_2);
angle2 = acosd(dot_product2);

% Determine if angle is above or below horizontal
if y2(3) < y2(1)
    angle_direction2 = 'upward';
else
    angle_direction2 = 'downward';
    % Keep angle positive for consistency
end

% Display angle on second image
text(x2(1)+10, y2(1)-20, [num2str(angle2, '%.1f') '°'], 'Color', 'green', 'FontSize', 14, 'FontWeight', 'bold');
hold off;

% Calculate total range of motion
% If both angles are in the same direction, subtract; if opposite, add
if strcmp(angle_direction1, angle_direction2)
    range_of_motion = abs(angle1 - angle2);
    motion_type = 'within same direction';
else
    range_of_motion = angle1 + angle2;
    motion_type = 'from upward to downward tilt';
end

% Create summary figure with both images
resultsFig = figure('Name', 'Head Angle Analysis Results', 'Position', [100 100 1000 600]);

% Add video file name and frame numbers to the title
displayFileName = strrep(videoFileName, '_', '\_');
sgtitle({['Source: ' displayFileName], ...
         ['Head Rotation: ' num2str(range_of_motion, '%.1f') '° range of motion'], ...
         ['(' motion_type ')']});

subplot(1,2,1);
imshow(img1); 
title({['Position 1: ' num2str(angle1, '%.1f') '° (' angle_direction1 ')'], ['Frame #' num2str(frameNum1)]});
hold on;
plot(x1(1), y1(1), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
plot(x1(2), y1(2), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
plot(x1(3), y1(3), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
line([x1(1) x1(2)], [y1(1) y1(2)], 'Color', 'b', 'LineWidth', 2);
line([x1(1) x1(3)], [y1(1) y1(3)], 'Color', 'r', 'LineWidth', 2);
hold off;

subplot(1,2,2);
imshow(img2); 
title({['Position 2: ' num2str(angle2, '%.1f') '° (' angle_direction2 ')'], ['Frame #' num2str(frameNum2)]});
hold on;
plot(x2(1), y2(1), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
plot(x2(2), y2(2), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
plot(x2(3), y2(3), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
line([x2(1) x2(2)], [y2(1) y2(2)], 'Color', 'b', 'LineWidth', 2);
line([x2(1) x2(3)], [y2(1) y2(3)], 'Color', 'r', 'LineWidth', 2);
hold off;

% Save the figure as an image
outputImageName = fullfile(videoPath, [baseFileName '_angle_analysis.png']);
saveas(resultsFig, outputImageName);
fprintf('Analysis image saved as: %s\n', outputImageName);

% Display results in command window
fprintf('\nHead Rotation Angle Results:\n');
fprintf('Video file: %s\n', videoFileName);
fprintf('Position 1 (Frame #%d): %.1f° (%s)\n', frameNum1, angle1, angle_direction1);
fprintf('Position 2 (Frame #%d): %.1f° (%s)\n', frameNum2, angle2, angle_direction2);
fprintf('Total range of motion: %.1f° (%s)\n', range_of_motion, motion_type);

% Add the callback function at the end of your script
function keyPressed(src, event, videoObj, imHandle)
    % Get current frame from figure's UserData
    currentFrame = get(src, 'UserData');
    selectedFrameNumbers = getappdata(src, 'selectedFrameNumbers');
    if isempty(selectedFrameNumbers)
        selectedFrameNumbers = zeros(1,2);
    end
    
    switch event.Key
        case 'rightarrow'
            % Move to next frame
            currentFrame = min(currentFrame + 1, videoObj.NumFrames);
        case 'leftarrow'
            % Move to previous frame
            currentFrame = max(currentFrame - 1, 1);
        case 'space'
            % Get frame count from figure's ApplicationData
            frameCount = getappdata(src, 'frameCount');
            if isempty(frameCount)
                frameCount = 0;
            end
            selectedFrames = getappdata(src, 'selectedFrames');
            if isempty(selectedFrames)
                selectedFrames = cell(1,2);
            end
            
            % Select current frame
            if frameCount < 2
                frameCount = frameCount + 1;
                selectedFrames{frameCount} = read(videoObj, currentFrame);
                fprintf('Frame %d selected (%d/2)\n', currentFrame, frameCount);
                
                % Store selected frames and frame numbers
                setappdata(src, 'selectedFrames', selectedFrames);
                setappdata(src, 'frameCount', frameCount);
                
                % Store frame number
                selectedFrameNumbers(frameCount) = currentFrame;
                setappdata(src, 'selectedFrameNumbers', selectedFrameNumbers);
                
                if frameCount == 2
                    fprintf('Two frames selected. Continuing with angle measurement...\n');
                    % Save selected frames for use outside the callback
                    assignin('base', 'selectedFrame1', selectedFrames{1});
                    assignin('base', 'selectedFrame2', selectedFrames{2});
                    assignin('base', 'selectedFrameNumbers', selectedFrameNumbers);
                    uiresume(src);
                    close(src);
                    return;
                end
            end
    end
    
    % Update current frame in UserData
    set(src, 'UserData', currentFrame);
    
    % Update display
    frame = read(videoObj, currentFrame);
    set(imHandle, 'CData', frame);
    title(sprintf('Frame %d / %d - Press → to advance, ← to go back, Space to select (%d/2)', ...
        currentFrame, videoObj.NumFrames, getappdata(src, 'frameCount')));
end