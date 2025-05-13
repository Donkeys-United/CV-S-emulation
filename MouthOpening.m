function measureMouthOpening(imagePath)
    % Load the image if path is provided, otherwise use UI to select
    if nargin < 1
        [fileName, pathName] = uigetfile({'*.jpg;*.jpeg;*.png;*.tif;*.bmp', 'Image Files'}, 'Select Image');
        if fileName == 0
            disp('Operation cancelled');
            return;
        end
        imagePath = fullfile(pathName, fileName);
    end
    
    % Extract original filename for later use in saving
    [pathStr, nameOnly, ext] = fileparts(imagePath);
    originalFileName = [nameOnly ext];
    
    % Read the image
    img = imread(imagePath);
    
    % Get screen size for proper window sizing
    screenSize = get(0, 'ScreenSize');
    screenWidth = screenSize(3);
    screenHeight = screenSize(4);
    
    % Create the main figure with maximized size
    fig = figure('Name', ['Figure 1: Mouth Opening Measurement - ' originalFileName], ...
                 'Position', [screenWidth*0.05, screenHeight*0.05, screenWidth*0.9, screenHeight*0.85], ...
                 'Units', 'normalized', ...
                 'MenuBar', 'none', ...
                 'ToolBar', 'none');
    
    % ----- UI ELEMENTS POSITIONED AS REQUESTED -----
    
    % Add filename display as an edit box to properly handle underscores
    filenameDisplay = uicontrol('Style', 'edit', ...
                               'String', ['Original image: ' originalFileName], ...
                               'Units', 'normalized', 'Position', [0.26, 0.96, 0.3, 0.03], ...
                               'HorizontalAlignment', 'left', ...
                               'FontSize', 9, ...
                               'Enable', 'inactive', ...
                               'BackgroundColor', get(fig, 'Color'), ...
                               'Tag', 'filenameDisplay');
    
    % Image orientation panel - left side of top row
    orientPanel = uipanel('Title', 'Image Orientation', ...
                          'Units', 'normalized', 'Position', [0.01, 0.87, 0.24, 0.08], ...
                          'Tag', 'orientPanel');
                     
    % Zoom controls panel - center-left of top row
    zoomPanel = uipanel('Title', 'Zoom Controls', ...
                        'Units', 'normalized', 'Position', [0.26, 0.87, 0.24, 0.08], ...
                        'Tag', 'zoomPanel');
                   
    % Magnifier panel - center-right of top row
    magPanel = uipanel('Title', 'Magnifier', ...
                       'Units', 'normalized', 'Position', [0.51, 0.87, 0.24, 0.08], ...
                       'Tag', 'magPanel');
                  
    % Actions panel - right side of top row
    actionsPanel = uipanel('Title', 'Actions', ...
                           'Units', 'normalized', 'Position', [0.76, 0.87, 0.23, 0.08], ...
                           'Tag', 'actionsPanel');
    
    % Bottom info panel
    infoPanel = uipanel('Title', 'Measurement Information', ...
                        'Units', 'normalized', 'Position', [0.01, 0.01, 0.98, 0.07], ...
                        'Tag', 'infoPanel');
    
    % Main image panel 
    mainPanel = uipanel('Units', 'normalized', 'Position', [0.01, 0.14, 0.98, 0.72], ...
                       'Tag', 'mainPanel');
    ax = axes('Parent', mainPanel, 'Position', [0, 0, 1, 1], 'Tag', 'mainAxes');
    
    % Add contents to Image Orientation panel
    uicontrol('Parent', orientPanel, 'Style', 'pushbutton', 'String', 'Flip Hor', ...
              'Units', 'normalized', 'Position', [0.05, 0.5, 0.4, 0.4], ...
              'Callback', @flipHorizontal, 'Tag', 'flipHorButton');
    uicontrol('Parent', orientPanel, 'Style', 'pushbutton', 'String', 'Flip Ver', ...
              'Units', 'normalized', 'Position', [0.5, 0.5, 0.4, 0.4], ...
              'Callback', @flipVertical, 'Tag', 'flipVerButton');
    uicontrol('Parent', orientPanel, 'Style', 'pushbutton', 'String', '↺ 90° CCW', ...
              'Units', 'normalized', 'Position', [0.05, 0.05, 0.4, 0.4], ...
              'Callback', @rotateLeft, 'Tag', 'rotateCCWButton');
    uicontrol('Parent', orientPanel, 'Style', 'pushbutton', 'String', '↻ 90° CW', ...
              'Units', 'normalized', 'Position', [0.5, 0.05, 0.4, 0.4], ...
              'Callback', @rotateRight, 'Tag', 'rotateCWButton');
    
    % Add contents to Zoom panel
    uicontrol('Parent', zoomPanel, 'Style', 'pushbutton', 'String', '🔍+', ...
              'Units', 'normalized', 'Position', [0.05, 0.2, 0.25, 0.6], ...
              'FontSize', 12, 'Callback', @zoomIn, 'Tag', 'zoomInButton');
    uicontrol('Parent', zoomPanel, 'Style', 'pushbutton', 'String', '🔍-', ...
              'Units', 'normalized', 'Position', [0.35, 0.2, 0.25, 0.6], ...
              'FontSize', 12, 'Callback', @zoomOut, 'Tag', 'zoomOutButton');
    uicontrol('Parent', zoomPanel, 'Style', 'pushbutton', 'String', 'Reset Zoom', ...
              'Units', 'normalized', 'Position', [0.65, 0.2, 0.3, 0.6], ...
              'Callback', @resetZoom, 'Tag', 'resetZoomButton');
    
    % Add contents to Magnifier panel
    uicontrol('Parent', magPanel, 'Style', 'togglebutton', 'String', 'Magnifier Mode', ...
              'Units', 'normalized', 'Position', [0.05, 0.2, 0.5, 0.6], ...
              'Callback', @toggleMagnifier, 'Tag', 'magModeButton');
    uicontrol('Parent', magPanel, 'Style', 'text', 'String', 'Size:', ...
              'Units', 'normalized', 'Position', [0.58, 0.4, 0.12, 0.3], ...
              'HorizontalAlignment', 'right', 'Tag', 'magSizeLabel');
    magSizeSlider = uicontrol('Parent', magPanel, 'Style', 'slider', ...
                              'Min', 50, 'Max', 200, 'Value', 100, ...
                              'Units', 'normalized', 'Position', [0.72, 0.4, 0.23, 0.3], ...
                              'Callback', @updateMagnifierSize, 'Tag', 'magSizeSlider');
    
    % Add Start Measurement button to Actions panel
    startButton = uicontrol('Parent', actionsPanel, 'Style', 'pushbutton', ...
                           'String', 'Start Measurement', ...
                           'Units', 'normalized', 'Position', [0.1, 0.2, 0.8, 0.6], ...
                           'FontWeight', 'bold', 'FontSize', 10, ...
                           'Callback', @startMeasurement, 'Tag', 'startButton');
    
    % Use edit box for measurement info to handle underscores properly
    measureText = uicontrol('Parent', infoPanel, 'Style', 'edit', ...
                           'Units', 'normalized', 'Position', [0.01, 0.1, 0.98, 0.8], ...
                           'HorizontalAlignment', 'left', ...
                           'String', ['Original Image: ' originalFileName ' | Calibration: Not yet performed'], ...
                           'Enable', 'inactive', ...
                           'Max', 2, ... % Allow multiple lines
                           'BackgroundColor', get(infoPanel, 'BackgroundColor'), ...
                           'Tag', 'measureText');
    
    % Display the image
    imshow(img, 'Parent', ax);
    
    % Create magnifier panel with IMPROVED DESIGN
    magPanel2 = uipanel('Parent', fig, 'Title', 'Magnified View', ...
                       'Units', 'normalized', 'Position', [0.7, 0.4, 0.25, 0.35], ...
                       'Visible', 'off', 'Tag', 'magnifierView');
    
    % Title for the magnifier
    magTitle = uicontrol('Parent', magPanel2, 'Style', 'text', ...
                        'Units', 'normalized', 'Position', [0.05, 0.9, 0.9, 0.08], ...
                        'String', 'Position: (0, 0)', ...
                        'HorizontalAlignment', 'center', 'Tag', 'magViewTitle');
    
    % Magnifier axes
    magAx = axes('Parent', magPanel2, 'Position', [0.05, 0.05, 0.9, 0.82], 'Tag', 'magAxes');
    
    % Storage for calibration and measurement data
    userData = struct();
    userData.img = img;
    userData.originalFileName = originalFileName;
    userData.calibrationPoints = [];
    userData.calibrationDistance = 0;
    userData.mouthPoints = [];
    userData.pixelsPerCm = 0;
    userData.mouthHeightCm = 0;
    userData.currentStep = 'rotate';
    userData.magnifierMode = false;
    userData.magnifierSize = 100;
    
    % Create zoom object for proper zoom functionality
    zoomObj = zoom(fig);
    
    % Store reference to UI elements
    userData.zoomObj = zoomObj;
    userData.magTitle = magTitle;
    userData.magAx = magAx;
    userData.magPanel2 = magPanel2;
    userData.filenameDisplay = filenameDisplay;
    userData.measureText = measureText;
    setappdata(fig, 'UserData', userData);
    
    % Make figure visible and maximize
    figure(fig);
    if ispc
        % For Windows
        set(fig, 'WindowState', 'maximized');
    else
        drawnow;
        pause(0.1);
        set(fig, 'Position', get(0, 'ScreenSize'));
    end
    
    % Add a toggle button for layout adjustment mode
    layoutToggle = uicontrol('Style', 'togglebutton', ...
                            'String', 'Layout Editor', ...
                            'Units', 'normalized', ...
                            'Position', [0.80, 0.95, 0.08, 0.03], ...
                            'Callback', @toggleLayoutEditor, ...
                            'Tag', 'layoutToggle');
    
    % Ensure the Toggle Layout Editor button is on top
    uistack(layoutToggle, 'top');
    
    function toggleLayoutEditor(src, ~)
        if get(src, 'Value')
            % Start layout editor
            createLayoutEditor();
        else
            % Close layout editor if exists
            layoutEditor = findobj(fig, 'Tag', 'layoutEditorPanel');
            if ~isempty(layoutEditor)
                delete(layoutEditor);
            end
        end
    end
    
    % UPDATED Layout Editor Creation Function
    function createLayoutEditor()
        % Create the layout editor panel
        editorPanel = uipanel('Title', 'Layout Editor', ...
                             'Units', 'normalized', 'Position', [0.15, 0.4, 0.3, 0.5], ...
                             'Tag', 'layoutEditorPanel');
        
        % Component selection dropdown
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, 0.93, 0.4, 0.05], ...
                 'String', 'Select Component:', 'HorizontalAlignment', 'left');
        
        % Get all components with tags
        allComponents = findall(fig, '-property', 'Tag');
        tags = get(allComponents, 'Tag');
        
        % Filter out empty tags and sort
        if iscell(tags)
            validIdx = ~cellfun(@isempty, tags);
            validComponents = allComponents(validIdx);
            validTags = tags(validIdx);
        else
            validTags = {tags};
            validComponents = allComponents;
        end
        
        % Create dropdown menu
        componentDropdown = uicontrol('Parent', editorPanel, 'Style', 'popupmenu', ...
                                     'Units', 'normalized', 'Position', [0.05, 0.85, 0.9, 0.07], ...
                                     'String', validTags, 'Callback', @selectComponent, ...
                                     'Value', 1);
        
        % Position adjustment sliders
        textHeight = 0.05;
        sliderHeight = 0.05;
        spacing = 0.03;
        yPos = 0.78;
        
        % Left Position Control
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, yPos, 0.15, textHeight], ...
                 'String', 'Left:', 'HorizontalAlignment', 'left');
        yPos = yPos - textHeight - 0.01;
        leftSlider = uicontrol('Parent', editorPanel, 'Style', 'slider', ...
                              'Units', 'normalized', 'Position', [0.05, yPos, 0.9, sliderHeight], ...
                              'Min', 0, 'Max', 1, 'Value', 0.5, 'Tag', 'leftSlider', ...
                              'Callback', @updatePosition);
        yPos = yPos - sliderHeight - spacing;
        
        % Bottom Position Control
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, yPos, 0.15, textHeight], ...
                 'String', 'Bottom:', 'HorizontalAlignment', 'left');
        yPos = yPos - textHeight - 0.01;
        bottomSlider = uicontrol('Parent', editorPanel, 'Style', 'slider', ...
                                'Units', 'normalized', 'Position', [0.05, yPos, 0.9, sliderHeight], ...
                                'Min', 0, 'Max', 1, 'Value', 0.5, 'Tag', 'bottomSlider', ...
                                'Callback', @updatePosition);
        yPos = yPos - sliderHeight - spacing;
        
        % Width Control
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, yPos, 0.15, textHeight], ...
                 'String', 'Width:', 'HorizontalAlignment', 'left');
        yPos = yPos - textHeight - 0.01;
        widthSlider = uicontrol('Parent', editorPanel, 'Style', 'slider', ...
                               'Units', 'normalized', 'Position', [0.05, yPos, 0.9, sliderHeight], ...
                               'Min', 0.01, 'Max', 1, 'Value', 0.5, 'Tag', 'widthSlider', ...
                               'Callback', @updatePosition);
        yPos = yPos - sliderHeight - spacing;
        
        % Height Control
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, yPos, 0.15, textHeight], ...
                 'String', 'Height:', 'HorizontalAlignment', 'left');
        yPos = yPos - textHeight - 0.01;
        heightSlider = uicontrol('Parent', editorPanel, 'Style', 'slider', ...
                                'Units', 'normalized', 'Position', [0.05, yPos, 0.9, sliderHeight], ...
                                'Min', 0.01, 'Max', 1, 'Value', 0.5, 'Tag', 'heightSlider', ...
                                'Callback', @updatePosition);
        yPos = yPos - sliderHeight - spacing;
        
        % Display current position
        positionText = uicontrol('Parent', editorPanel, 'Style', 'text', ...
                                'Units', 'normalized', 'Position', [0.05, yPos, 0.9, textHeight*2], ...
                                'String', 'Position: [0 0 0 0]', 'HorizontalAlignment', 'left', ...
                                'Tag', 'positionText');
        yPos = yPos - textHeight*2 - spacing;
        
        % Code output
        uicontrol('Parent', editorPanel, 'Style', 'text', ...
                 'Units', 'normalized', 'Position', [0.05, yPos, 0.9, textHeight], ...
                 'String', 'Generated Code:', 'HorizontalAlignment', 'left');
        yPos = yPos - textHeight - 0.01;
        codeOutput = uicontrol('Parent', editorPanel, 'Style', 'edit', ...
                              'Units', 'normalized', 'Position', [0.05, yPos-0.15, 0.9, 0.15], ...
                              'Min', 1, 'Max', 5, 'HorizontalAlignment', 'left', ...
                              'BackgroundColor', [1 1 1], 'Tag', 'codeOutput');
        yPos = yPos - 0.15 - spacing;
        
        % Highlight components button
        uicontrol('Parent', editorPanel, 'Style', 'pushbutton', ...
                 'Units', 'normalized', 'Position', [0.05, 0.05, 0.4, 0.06], ...
                 'String', 'Highlight All Components', 'Callback', @highlightComponents);
        
        % Apply button - NEW: Adding this button for direct application
        uicontrol('Parent', editorPanel, 'Style', 'pushbutton', ...
                 'Units', 'normalized', 'Position', [0.5, 0.05, 0.4, 0.06], ...
                 'String', 'Apply Changes', 'BackgroundColor', [0.8, 1, 0.8], ...
                 'Callback', @applyChanges);
        
        % Store component information directly in appdata
        setappdata(editorPanel, 'Components', validComponents);
        setappdata(editorPanel, 'Tags', validTags);
        setappdata(editorPanel, 'SelectedComponent', validComponents(1));
        setappdata(editorPanel, 'SelectedIndex', 1);
        setappdata(editorPanel, 'Highlight', []);
        
        % Store control references
        setappdata(editorPanel, 'LeftSlider', leftSlider);
        setappdata(editorPanel, 'BottomSlider', bottomSlider);
        setappdata(editorPanel, 'WidthSlider', widthSlider);
        setappdata(editorPanel, 'HeightSlider', heightSlider);
        setappdata(editorPanel, 'PositionText', positionText);
        setappdata(editorPanel, 'CodeOutput', codeOutput);
        
        % Initial selection
        selectComponent(componentDropdown, []);
        
        % Component selection callback
        function selectComponent(src, ~)
            idx = get(src, 'Value');
            
            if idx > 0 && idx <= length(validComponents)
                % Set currently selected component
                comp = validComponents(idx);
                setappdata(editorPanel, 'SelectedComponent', comp);
                setappdata(editorPanel, 'SelectedIndex', idx);
                
                % Get current position
                try
                    pos = get(comp, 'Position');
                    
                    % Only update if position is valid
                    if length(pos) == 4
                        % Update sliders without triggering callbacks
                        set(leftSlider, 'Value', pos(1));
                        set(bottomSlider, 'Value', pos(2));
                        set(widthSlider, 'Value', pos(3));
                        set(heightSlider, 'Value', pos(4));
                        
                        % Update text displays
                        updatePositionText(pos);
                        updateCodeOutput(pos);
                        
                        % Highlight the selected component
                        highlightSelectedComponent();
                    else
                        set(positionText, 'String', 'Invalid position property');
                    end
                catch e
                    disp(['Error getting position: ' e.message]);
                    set(positionText, 'String', 'Error getting position');
                end
            end
        end
        
        % Position update callback - FIXED
        function updatePosition(src, ~)
            try
                % Get the currently selected component
                comp = getappdata(editorPanel, 'SelectedComponent');
                
                if ~isempty(comp) && ishandle(comp)
                    % Get values from sliders
                    newPos = [
                        get(leftSlider, 'Value'),
                        get(bottomSlider, 'Value'),
                        get(widthSlider, 'Value'),
                        get(heightSlider, 'Value')
                    ];
                    
                    % Update text displays
                    updatePositionText(newPos);
                    updateCodeOutput(newPos);
                    
                    % Draw preview without actually changing the component yet
                    highlightSelectedComponent(newPos);
                end
            catch e
                disp(['Error updating position: ' e.message]);
            end
        end
        
        % NEW: Apply changes button callback
        function applyChanges(~, ~)
            try
                % Get the currently selected component
                comp = getappdata(editorPanel, 'SelectedComponent');
                
                if ~isempty(comp) && ishandle(comp)
                    % Get values from sliders
                    newPos = [
                        get(leftSlider, 'Value'),
                        get(bottomSlider, 'Value'),
                        get(widthSlider, 'Value'),
                        get(heightSlider, 'Value')
                    ];
                    
                    % Set the new position
                    set(comp, 'Position', newPos);
                    
                    % Update highlight
                    highlightSelectedComponent();
                    
                    % Flash the component briefly to indicate change
                    flashComponent(comp);
                end
            catch e
                disp(['Error applying changes: ' e.message]);
            end
        end
        
        % Flash component to show it's been updated
        function flashComponent(comp)
            try
                originalColor = get(comp, 'BackgroundColor');
                set(comp, 'BackgroundColor', [0, 1, 0]); % Flash green
                pause(0.2);
                set(comp, 'BackgroundColor', originalColor);
            catch
                % If we can't change background color, just skip the effect
            end
        end
        
        % Update position text display
        function updatePositionText(pos)
            set(positionText, 'String', sprintf('Position: [%.3f %.3f %.3f %.3f]', pos));
        end
        
        % Update code output
        function updateCodeOutput(pos)
            idx = getappdata(editorPanel, 'SelectedIndex');
            tag = validTags{idx};
            
            code = sprintf('set(findobj(gcf, ''Tag'', ''%s''), ''Position'', [%.3f %.3f %.3f %.3f]);', ...
                          tag, pos(1), pos(2), pos(3), pos(4));
            set(codeOutput, 'String', code);
        end
        
        % Highlight the selected component - FIXED
        function highlightSelectedComponent(previewPos)
            % Remove previous highlight
            highlight = getappdata(editorPanel, 'Highlight');
            if ~isempty(highlight) && ishandle(highlight)
                delete(highlight);
            end
            
            % Get the selected component
            comp = getappdata(editorPanel, 'SelectedComponent');
            
            if ~isempty(comp) && ishandle(comp)
                % Use provided preview position if available, otherwise use current position
                if nargin < 1
                    pos = get(comp, 'Position');
                else
                    pos = previewPos;
                end
                
                % Create a rectangle around the component
                figure(fig); % Make sure we're drawing on the main figure
                
                % Create new highlight rectangle
                h = annotation('rectangle', pos, 'Color', 'r', 'LineWidth', 2, 'LineStyle', '-');
                setappdata(editorPanel, 'Highlight', h);
            end
        end
        
        % Highlight all components
        function highlightComponents(~, ~)
            % Get all components
            components = findall(fig, '-property', 'Position');
            
            % Remove any existing highlight rectangles
            oldHighlights = findall(fig, 'Tag', 'highlight');
            delete(oldHighlights);
            
            % Create a figure for the legend
            legendFig = figure('Name', 'Component Tags', ...
                              'NumberTitle', 'off', ...
                              'Position', [100, 100, 300, 400], ...
                              'MenuBar', 'none', 'ToolBar', 'none');
            
            % Create a listbox for the tags
            listbox = uicontrol('Parent', legendFig, 'Style', 'listbox', ...
                               'Units', 'normalized', 'Position', [0.05, 0.05, 0.9, 0.9], ...
                               'String', {});
            
            % Initialize the tag list
            tagList = {};
            colors = jet(length(components));
            
            % Add highlights for each component
            for i = 1:length(components)
                comp = components(i);
                
                % Skip if not a valid component
                if strcmp(get(comp, 'Type'), 'figure') || ~isvalid(comp)
                    continue;
                end
                
                % Get tag and position
                tag = get(comp, 'Tag');
                if isempty(tag)
                    tag = ['Unnamed_' num2str(i)];
                end
                
                pos = get(comp, 'Position');
                
                % Skip if position is empty
                if isempty(pos) || length(pos) ~= 4
                    continue;
                end
                
                % Choose color for this component
                color = colors(mod(i-1, size(colors, 1))+1, :);
                
                % Create annotation directly on the figure
                figure(fig);
                rect = annotation('rectangle', pos, 'Color', color, 'LineWidth', 1.5, 'Tag', 'highlight');
                
                % Add tag to list with color indicator
                tagList{end+1} = sprintf('[%.2f, %.2f, %.2f] - %s', color, tag);
            end
            
            % Update listbox
            set(listbox, 'String', tagList);
            
            % Add close button to remove highlights
            uicontrol('Parent', legendFig, 'Style', 'pushbutton', ...
                     'Units', 'normalized', 'Position', [0.25, 0.01, 0.5, 0.04], ...
                     'String', 'Close & Remove Highlights', ...
                     'Callback', @(~,~) closeHighlights());
            
            function closeHighlights()
                % Remove highlights
                delete(findall(fig, 'Tag', 'highlight'));
                % Close legend
                close(legendFig);
            end
        end
    end
    
    % Callback function for 90° counterclockwise rotation
    function rotateLeft(~, ~)
        userData = getappdata(fig, 'UserData');
        userData.img = rot90(userData.img);
        imshow(userData.img, 'Parent', ax);
        setappdata(fig, 'UserData', userData);
    end

    % Callback function for 90° clockwise rotation
    function rotateRight(~, ~)
        userData = getappdata(fig, 'UserData');
        userData.img = rot90(userData.img, -1);
        imshow(userData.img, 'Parent', ax);
        setappdata(fig, 'UserData', userData);
    end
    
    % Callback function for horizontal flip
    function flipHorizontal(~, ~)
        userData = getappdata(fig, 'UserData');
        userData.img = fliplr(userData.img);
        imshow(userData.img, 'Parent', ax);
        setappdata(fig, 'UserData', userData);
    end
    
    % Callback function for vertical flip
    function flipVertical(~, ~)
        userData = getappdata(fig, 'UserData');
        userData.img = flipud(userData.img);
        imshow(userData.img, 'Parent', ax);
        setappdata(fig, 'UserData', userData);
    end
    
    % Zoom functions
    function zoomIn(~, ~)
        userData = getappdata(fig, 'UserData');
        
        % Disable other interactive modes if active
        if userData.magnifierMode
            set(userData.magPanel2, 'Visible', 'off');
            set(fig, 'WindowButtonMotionFcn', '');
            userData.magnifierMode = false;
            setappdata(fig, 'UserData', userData);
        end
        
        % Properly enable zoom mode
        set(userData.zoomObj, 'Enable', 'on', 'Direction', 'in');
        set(userData.zoomObj, 'ActionPostCallback', @onZoomChange);
    end
    
    function zoomOut(~, ~)
        userData = getappdata(fig, 'UserData');
        
        % Disable other interactive modes if active
        if userData.magnifierMode
            set(userData.magPanel2, 'Visible', 'off');
            set(fig, 'WindowButtonMotionFcn', '');
            userData.magnifierMode = false;
            setappdata(fig, 'UserData', userData);
        end
        
        % Properly enable zoom mode
        set(userData.zoomObj, 'Enable', 'on', 'Direction', 'out');
        set(userData.zoomObj, 'ActionPostCallback', @onZoomChange);
    end
    
    function resetZoom(~, ~)
        userData = getappdata(fig, 'UserData');
        
        % Disable other interactive modes if active
        if userData.magnifierMode
            set(userData.magPanel2, 'Visible', 'off');
            set(fig, 'WindowButtonMotionFcn', '');
            userData.magnifierMode = false;
            setappdata(fig, 'UserData', userData);
        end
        
        % Reset the axes limits to default
        axis(ax, 'auto');
        imshow(userData.img, 'Parent', ax);
    end
    
    function onZoomChange(~, ~)
        % Optional callback after zoom completes
    end
    
    % Toggle magnifier mode
    function toggleMagnifier(src, ~)
        userData = getappdata(fig, 'UserData');
        userData.magnifierMode = get(src, 'Value');
        
        if userData.magnifierMode
            % Disable zoom if it's active
            set(userData.zoomObj, 'Enable', 'off');
            
            % Setup magnifier movement tracking
            set(userData.magPanel2, 'Visible', 'on');
            set(fig, 'WindowButtonMotionFcn', @updateMagnifier);
        else
            % Turn off magnifier
            set(userData.magPanel2, 'Visible', 'off');
            set(fig, 'WindowButtonMotionFcn', '');
        end
        
        setappdata(fig, 'UserData', userData);
    end
    
    % Update magnifier size
    function updateMagnifierSize(src, ~)
        userData = getappdata(fig, 'UserData');
        userData.magnifierSize = get(src, 'Value');
        setappdata(fig, 'UserData', userData);
        
        if userData.magnifierMode
            updateMagnifier();
        end
    end
    
    % IMPROVED MAGNIFIER FUNCTION WITH CENTER POINT INDICATOR
    function updateMagnifier(~, ~)
        userData = getappdata(fig, 'UserData');
        
        try
            % Get current cursor position
            cp = get(ax, 'CurrentPoint');
            x = round(cp(1,1));
            y = round(cp(1,2));
            
            % Get image dimensions
            [imgHeight, imgWidth, ~] = size(userData.img);
            
            % Check if cursor is within the image
            if x >= 1 && x <= imgWidth && y >= 1 && y <= imgHeight
                % Set up magnifier window size
                magSize = round(userData.magnifierSize / 2);
                
                % Determine the region to extract
                xRange = max(1, x-magSize):min(imgWidth, x+magSize);
                yRange = max(1, y-magSize):min(imgHeight, y+magSize);
                
                % Extract sub-image
                if ~isempty(xRange) && ~isempty(yRange)
                    subImg = userData.img(yRange, xRange, :);
                    
                    % Display in magnifier axes
                    imshow(subImg, 'Parent', userData.magAx);
                    
                    % Update position text
                    set(userData.magTitle, 'String', sprintf('Position: (%d, %d)', x, y));
                    
                    % Add a red dot at the center of the magnifier to indicate the selection point
                    hold(userData.magAx, 'on');
                    centerX = size(subImg, 2) / 2;
                    centerY = size(subImg, 1) / 2;
                    plot(userData.magAx, centerX, centerY, 'r.', 'MarkerSize', 10);
                    hold(userData.magAx, 'off');
                    
                    % Keep magnifier visible
                    set(userData.magPanel2, 'Visible', 'on');
                end
            end
        catch err
            % Error handling to prevent crashes
            disp(['Magnifier error: ' err.message]);
        end
    end

    % Main measurement workflow
    function startMeasurement(~, ~)
        userData = getappdata(fig, 'UserData');
        
        % Disable zoom and magnifier if active
        set(userData.zoomObj, 'Enable', 'off');
        if userData.magnifierMode
            set(userData.magPanel2, 'Visible', 'off');
            set(fig, 'WindowButtonMotionFcn', '');
            userData.magnifierMode = false;
        end
        
        userData.currentStep = 'calibration';
        setappdata(fig, 'UserData', userData);
        
        % Reset the plot for measurement
        imshow(userData.img, 'Parent', ax);
        hold(ax, 'on');
        
        % Start calibration procedure
        title(ax, 'Select two points on the measuring tape with a known distance between them');
        
        % Use set() with direct string instead of strrep
        set(userData.measureText, 'String', ['Original Image: ' userData.originalFileName ' | Step 1: Select two points on the measuring tape']);
        
        userData.calibrationPoints = [];
        setappdata(fig, 'UserData', userData);
        
        % Set up mouse click callback for calibration
        set(fig, 'WindowButtonDownFcn', @calibrationClick);
    end
    
    % Callback for calibration clicks
    function calibrationClick(~, ~)
        userData = getappdata(fig, 'UserData');
        
        if strcmp(userData.currentStep, 'calibration')
            cp = get(ax, 'CurrentPoint');
            x = cp(1,1);
            y = cp(1,2);
            
            xlim = get(ax, 'XLim');
            ylim = get(ax, 'YLim');
            
            % Check if click is within the image bounds
            if x >= xlim(1) && x <= xlim(2) && y >= ylim(1) && y <= ylim(2)
                userData.calibrationPoints(end+1,:) = [x y];
                pointIndex = size(userData.calibrationPoints, 1);
                
                % Draw the point with correct numbering
                plot(ax, x, y, 'ro', 'MarkerSize', 8, 'LineWidth', 2);
                text(ax, x+50, y, ['Point ', num2str(pointIndex)], ...
                    'Color', 'r', 'FontWeight', 'bold');
                
                % If we have two points, proceed to distance input
                if pointIndex == 2
                    % Draw a line between the calibration points
                    plot(ax, userData.calibrationPoints(:,1), userData.calibrationPoints(:,2), 'r-', 'LineWidth', 1);
                    
                    % Prompt for distance
                    userData.currentStep = 'wait';
                    setappdata(fig, 'UserData', userData);
                    set(fig, 'WindowButtonDownFcn', '');
                    
                    % Ask for the distance
                    answer = inputdlg('Enter the distance between selected points (in cm):', ...
                        'Calibration', 1, {'10'});
                    
                    if isempty(answer)
                        % User cancelled, restart
                        title(ax, 'Calibration cancelled. Press "Start Measurement" to try again.');
                        set(userData.measureText, 'String', ['Original Image: ' userData.originalFileName ' | Calibration cancelled']);
                        return;
                    end
                    
                    userData = getappdata(fig, 'UserData');
                    userData.calibrationDistance = str2double(answer{1});
                    
                    if isnan(userData.calibrationDistance) || userData.calibrationDistance <= 0
                        % Invalid input, restart
                        title(ax, 'Invalid input. Press "Start Measurement" to try again.');
                        set(userData.measureText, 'String', ['Original Image: ' userData.originalFileName ' | Invalid distance input']);
                        return;
                    end
                    
                    % Calculate pixels per cm
                    p1 = userData.calibrationPoints(1,:);
                    p2 = userData.calibrationPoints(2,:);
                    distancePixels = sqrt((p2(1)-p1(1))^2 + (p2(2)-p1(2))^2);
                    userData.pixelsPerCm = distancePixels / userData.calibrationDistance;
                    
                    % Update the info text - FIXED underscore display
                    set(userData.measureText, 'String', sprintf('Original Image: %s | Calibration: %.2f pixels = 1 cm (Distance: %.2f cm)', ...
                        userData.originalFileName, userData.pixelsPerCm, userData.calibrationDistance));
                    
                    % Move to mouth measurement
                    userData.currentStep = 'mouth_top';
                    setappdata(fig, 'UserData', userData);
                    title(ax, 'Now select the top edge of the mouth opening');
                    set(fig, 'WindowButtonDownFcn', @mouthClick);
                end
            end
        end
        
        setappdata(fig, 'UserData', userData);
    end
    
    % Callback for mouth measurement clicks
    function mouthClick(~, ~)
        userData = getappdata(fig, 'UserData');
        
        cp = get(ax, 'CurrentPoint');
        x = cp(1,1);
        y = cp(1,2);
        
        xlim = get(ax, 'XLim');
        ylim = get(ax, 'YLim');
        
        % Check if click is within the image bounds
        if x >= xlim(1) && x <= xlim(2) && y >= ylim(1) && y <= ylim(2)
            if strcmp(userData.currentStep, 'mouth_top')
                % Store top point
                userData.mouthPoints(1,:) = [x y];
                
                % Draw horizontal line at top edge
                plot(ax, [xlim(1), xlim(2)], [y, y], 'g-', 'LineWidth', 2);
                
                % Move to bottom measurement
                userData.currentStep = 'mouth_bottom';
                title(ax, 'Select the bottom edge of the mouth opening');
                
            elseif strcmp(userData.currentStep, 'mouth_bottom')
                % Store bottom point
                userData.mouthPoints(2,:) = [x y];
                
                % Draw horizontal line at bottom edge
                plot(ax, [xlim(1), xlim(2)], [y, y], 'g-', 'LineWidth', 2);
                
                % Calculate the height of the mouth opening
                mouthHeightPixels = abs(userData.mouthPoints(2,2) - userData.mouthPoints(1,2));
                userData.mouthHeightCm = mouthHeightPixels / userData.pixelsPerCm;
                
                % Add vertical measurement line in the center of the image
                midX = mean(xlim);
                topY = userData.mouthPoints(1,2);
                bottomY = userData.mouthPoints(2,2);
                
                % Turn off magnifier if active
                if userData.magnifierMode
                    set(userData.magPanel2, 'Visible', 'off');
                    set(fig, 'WindowButtonMotionFcn', '');
                    userData.magnifierMode = false;
                end
                
                % Draw measurement line
                plot(ax, [midX, midX], [topY, bottomY], 'g-', 'LineWidth', 2);
                
                % Display the result
                title(ax, sprintf('Mouth Opening Height: %.2f cm', userData.mouthHeightCm));
                
                % Add a text label directly on top of the image
                textHandle = uicontrol('Style', 'text', ...
                    'Units', 'normalized', ...
                    'Position', [0.4, 0.8, 0.15, 0.035], ...
                    'String', sprintf('Mouth Opening: %.2f cm', userData.mouthHeightCm), ...
                    'BackgroundColor', 'white', ...
                    'FontSize', 12, ...
                    'FontWeight', 'bold', ...
                    'HorizontalAlignment', 'center');
                
                % Make sure it's on top
                uistack(textHandle, 'top');
                
                % Update the info text - FIXED underscore display
                set(userData.measureText, 'String', sprintf(['Original Image: %s | Calibration: %.2f pixels = 1 cm (Distance: %.2f cm) | ' ...
                    'Mouth Opening Height: %.2f cm'], userData.originalFileName, userData.pixelsPerCm, ...
                    userData.calibrationDistance, userData.mouthHeightCm));
                
                % Save the result with original filename reference
                userData.currentStep = 'completed';
                outputFilename = fullfile(pathStr, [nameOnly, '_measuring_result', ext]);
                
                % Add a watermark with original filename before saving - FIXED underscore handling
                dim = [.02 .95 .3 .03];
                annotation('textbox', dim, 'String', ['Original image: ' userData.originalFileName], ...
                          'FitBoxToText', 'on', 'BackgroundColor', 'white', ...
                          'EdgeColor', 'none', 'FontSize', 9);
                
                saveas(fig, outputFilename);
                
                % Inform user - FIXED underscore handling in message box
                msgbox(sprintf(['Measurement completed successfully.\n\n' ...
                    'Mouth Opening Height: %.2f cm\n\n' ...
                    'Results saved to: %s\n\n' ...
                    'Original image: %s'], userData.mouthHeightCm, outputFilename, userData.originalFileName), ...
                    'Measurement Complete');
                
                % Disable further clicks
                set(fig, 'WindowButtonDownFcn', '');
            end
        end
        
        setappdata(fig, 'UserData', userData);
    end
end