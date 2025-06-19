# eq_ui_model.py

class EQBase:
    """Base class for all EverQuest UI elements, handling common attributes like 'item'."""
    def __init__(self, item=None):
        self.item = item

class EQRGB(EQBase):
    """Represents an RGB color with an Alpha channel."""
    def __init__(self, r=0, g=0, b=0, alpha=255, item=None):
        super().__init__(item)
        self.r = r
        self.g = g
        self.b = b
        self.alpha = alpha

    def __repr__(self):
        return f"RGB(R={self.r}, G={self.g}, B={self.b}, A={self.alpha})"

    def to_tuple(self):
        return (self.r, self.g, self.b, self.alpha)

class EQPoint(EQBase):
    """Represents a 2D coordinate (X, Y)."""
    def __init__(self, x=0, y=0, item=None):
        super().__init__(item)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(X={self.x}, Y={self.y})"

    def to_tuple(self):
        return (self.x, self.y)

class EQSize(EQBase):
    """Represents dimensions (CX for width, CY for height)."""
    def __init__(self, cx=0, cy=0, item=None):
        super().__init__(item)
        self.cx = cx
        self.cy = cy

    def __repr__(self):
        return f"Size(CX={self.cx}, CY={self.cy})"

    def to_tuple(self):
        return (self.cx, self.cy)


class EQScreenPiece(EQBase):
    """Base class for all visible UI elements, with common position, size, and anchoring."""
    def __init__(self, screen_id=None, font=3, relative_position=True,
                 location=None, size=None,
                 auto_stretch=False, auto_stretch_vertical=False, auto_stretch_horizontal=False,
                 top_anchor_to_top=True, left_anchor_to_left=True, bottom_anchor_to_top=True, right_anchor_to_left=True,
                 top_anchor_offset=0, bottom_anchor_offset=0, left_anchor_offset=0, right_anchor_offset=0,
                 min_v_size=0, min_h_size=0, max_v_size=0, max_h_size=0,
                 text=None, text_color=None, disabled_color=None,
                 use_in_layout_horizontal=True, use_in_layout_vertical=True,
                 background_texture_tint=None, item=None):

        super().__init__(item)
        self.screen_id = screen_id
        self.font = font
        self.relative_position = relative_position

        # Initialize complex types as objects if not provided
        self.location = location if location is not None else EQPoint()
        self.size = size if size is not None else EQSize()
        self.text_color = text_color if text_color is not None else EQRGB(r=255, g=255, b=255) # Default white text
        self.disabled_color = disabled_color if disabled_color is not None else EQRGB() # Default black disabled text
        self.background_texture_tint = background_texture_tint if background_texture_tint is not None else EQRGB(r=255, g=255, b=255) # Default white tint

        self.auto_stretch = auto_stretch
        self.auto_stretch_vertical = auto_stretch_vertical
        self.auto_stretch_horizontal = auto_stretch_horizontal
        self.top_anchor_to_top = top_anchor_to_top
        self.left_anchor_to_left = left_anchor_to_left
        self.bottom_anchor_to_top = bottom_anchor_to_top
        self.right_anchor_to_left = right_anchor_to_left
        self.top_anchor_offset = top_anchor_offset
        self.bottom_anchor_offset = bottom_anchor_offset
        self.left_anchor_offset = left_anchor_offset
        self.right_anchor_offset = right_anchor_offset
        self.min_v_size = min_v_size
        self.min_h_size = min_h_size
        self.max_v_size = max_v_size
        self.max_h_size = max_h_size
        self.text = text
        self.use_in_layout_horizontal = use_in_layout_horizontal
        self.use_in_layout_vertical = use_in_layout_vertical

    def __repr__(self):
        return (f"ScreenPiece(ScreenID='{self.screen_id}', "
                f"Location={self.location}, Size={self.size}, Text='{self.text}')")

class EQControl(EQScreenPiece):
    """Base class for interactive UI elements, inheriting from ScreenPiece."""
    def __init__(self, eq_type=None, style_v_scroll=False, style_h_scroll=False,
                 style_auto_v_scroll=False, style_auto_h_scroll=False,
                 style_transparent=False, style_transparent_control=False,
                 style_border=False, style_tooltip=True, tooltip_reference=None,
                 draw_template=None, layout=None, item=None, **kwargs):
        super().__init__(item=item, **kwargs) # Pass kwargs to the parent (EQScreenPiece) constructor
        self.eq_type = eq_type
        self.style_v_scroll = style_v_scroll
        self.style_h_scroll = style_h_scroll
        self.style_auto_v_scroll = style_auto_v_scroll
        self.style_auto_h_scroll = style_auto_h_scroll
        self.style_transparent = style_transparent
        self.style_transparent_control = style_transparent_control
        self.style_border = style_border
        self.style_tooltip = style_tooltip
        self.tooltip_reference = tooltip_reference
        # draw_template and layout would be references to other complex objects
        self.draw_template = draw_template # Placeholder for now
        self.layout = layout # Placeholder for now

    def __repr__(self):
        return (f"Control(ScreenID='{self.screen_id}', EQType='{self.eq_type}', "
                f"Location={self.location}, Size={self.size})")

class EQStaticScreenPiece(EQScreenPiece):
    """Base class for non-interactive visual elements."""
    def __init__(self, auto_draw=True, item=None, **kwargs):
        super().__init__(item=item, **kwargs)
        self.auto_draw = auto_draw

    def __repr__(self):
        return f"StaticScreenPiece(ScreenID='{self.screen_id}', Text='{self.text}')"

class EQStaticText(EQStaticScreenPiece):
    """Represents a static text display."""
    def __init__(self, no_wrap=False, align_center=False, align_right=False, item=None, **kwargs):
        super().__init__(item=item, **kwargs)
        self.no_wrap = no_wrap
        self.align_center = align_center
        self.align_right = align_right

    def __repr__(self):
        return f"StaticText(ScreenID='{self.screen_id}', Text='{self.text}')"

class EQButton(EQControl):
    """Represents a clickable button."""
    def __init__(self, style_checkbox=False, radio_group=None, text=None,
                 mouseover_color=None, pressed_color=None,
                 use_custom_mouseover_color=False, use_custom_disabled_color=False, use_custom_pressed_color=False,
                 text_align_center=True, text_align_right=False, text_align_v_center=True,
                 text_offset_x=0, text_offset_y=0,
                 button_draw_template=None, template=None, # template is likely an alias or for named templates
                 sound_pressed=None, sound_up=None, sound_flyby=None,
                 decal_offset=None, decal_size=None,
                 item=None, **kwargs):
        super().__init__(item=item, **kwargs)
        self.style_checkbox = style_checkbox
        self.radio_group = radio_group
        self.text = text
        self.mouseover_color = mouseover_color if mouseover_color is not None else EQRGB()
        self.pressed_color = pressed_color if pressed_color is not None else EQRGB()
        self.use_custom_mouseover_color = use_custom_mouseover_color
        self.use_custom_disabled_color = use_custom_disabled_color
        self.use_custom_pressed_color = use_custom_pressed_color
        self.text_align_center = text_align_center
        self.text_align_right = text_align_right
        self.text_align_v_center = text_align_v_center
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.button_draw_template = button_draw_template # Placeholder for DrawTemplate object
        self.template = template # Placeholder for DrawTemplate object (for named templates)
        self.sound_pressed = sound_pressed
        self.sound_up = sound_up
        self.sound_flyby = sound_flyby
        self.decal_offset = decal_offset if decal_offset is not None else EQPoint()
        self.decal_size = decal_size if decal_size is not None else EQSize()

    def __repr__(self):
        return f"Button(ScreenID='{self.screen_id}', Text='{self.text}', Loc={self.location}, Size={self.size})"

class EQGauge(EQControl):
    """Represents a progress bar or gauge."""
    def __init__(self, gauge_draw_template=None, fill_tint=None,
                 draw_lines_fill=False, lines_fill_tint=None,
                 text_offset_x=0, text_offset_y=0,
                 gauge_offset_x=0, gauge_offset_y=16,
                 item=None, **kwargs):
        super().__init__(item=item, **kwargs)
        self.gauge_draw_template = gauge_draw_template # Placeholder for DrawTemplate object
        self.fill_tint = fill_tint if fill_tint is not None else EQRGB()
        self.draw_lines_fill = draw_lines_fill
        self.lines_fill_tint = lines_fill_tint if lines_fill_tint is not None else EQRGB()
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.gauge_offset_x = gauge_offset_x
        self.gauge_offset_y = gauge_offset_y

    def __repr__(self):
        return f"Gauge(ScreenID='{self.screen_id}', Loc={self.location}, Size={self.size})"

class EQLabel(EQControl):
    """Represents a display label, often for dynamic text."""
    def __init__(self, no_wrap=False, align_center=False, align_right=False,
                 resize_height_to_text=False, item=None, **kwargs):
        super().__init__(item=item, **kwargs)
        self.no_wrap = no_wrap
        self.align_center = align_center
        self.align_right = align_right
        self.resize_height_to_text = resize_height_to_text

    def __repr__(self):
        return f"Label(ScreenID='{self.screen_id}', Text='{self.text}', Loc={self.location}, Size={self.size})"

class EQWindow(EQControl): # SIDL.xml calls this 'Screen' but we'll use Window for clarity
    """Represents a top-level EverQuest UI window."""
    def __init__(self, style_titlebar=False, style_closebox=False, style_maximizebox=False,
                 style_qmarkbox=False, style_minimizebox=False, style_sizable=False,
                 style_sizable_border_top=True, style_sizable_border_bottom=True,
                 style_sizable_border_left=True, style_sizable_border_right=True,
                 style_sizable_border_top_left=True, style_sizable_border_top_right=True,
                 style_sizable_border_bottom_left=True, style_sizable_border_bottom_right=True,
                 style_client_movable=False, escapable=True, pieces=None, item=None, **kwargs):
        super().__init__(item=item, **kwargs) # Pass kwargs to the parent (EQControl) constructor
        self.style_titlebar = style_titlebar
        self.style_closebox = style_closebox
        self.style_maximizebox = style_maximizebox
        self.style_qmarkbox = style_qmarkbox
        self.style_minimizebox = style_minimizebox
        self.style_sizable = style_sizable
        self.style_sizable_border_top = style_sizable_border_top
        self.style_sizable_border_bottom = style_sizable_border_bottom
        self.style_sizable_border_left = style_sizable_border_left
        self.style_sizable_border_right = style_sizable_border_right
        self.style_sizable_border_top_left = style_sizable_border_top_left
        self.style_sizable_border_top_right = style_sizable_border_top_right
        self.style_sizable_border_bottom_left = style_sizable_border_bottom_left
        self.style_sizable_border_bottom_right = style_sizable_border_bottom_right
        self.style_client_movable = style_client_movable
        self.escapable = escapable
        self.pieces = pieces if pieces is not None else [] # A list to hold child ScreenPiece objects

    def __repr__(self):
        return (f"Window(ScreenID='{self.screen_id}', "
                f"Location={self.location}, Size={self.size}, "
                f"Children={len(self.pieces)} pieces)")