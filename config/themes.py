# Application themes and styling

# Modern color palette
COLORS = {
    "primary": {"light": "#3498db", "dark": "#2980b9"},
    "secondary": {"light": "#2ecc71", "dark": "#27ae60"},
    "accent": {"light": "#9b59b6", "dark": "#8e44ad"},
    "warning": {"light": "#f39c12", "dark": "#d35400"},
    "danger": {"light": "#e74c3c", "dark": "#c0392b"},
    "info": {"light": "#1abc9c", "dark": "#16a085"},
    "background": {"light": "#ecf0f1", "dark": "#2c3e50"},
    "surface": {"light": "#ffffff", "dark": "#34495e"},
    "text": {"light": "#2c3e50", "dark": "#ecf0f1"},
    "text_secondary": {"light": "#7f8c8d", "dark": "#bdc3c7"}
}

# Theme settings for CustomTkinter
def get_theme_settings(appearance_mode="light"):
    """
    Returns theme settings based on appearance mode
    """
    if appearance_mode == "dark":
        return {
            "color_primary": COLORS["primary"]["dark"],
            "color_secondary": COLORS["secondary"]["dark"],
            "color_accent": COLORS["accent"]["dark"],
            "color_warning": COLORS["warning"]["dark"],
            "color_danger": COLORS["danger"]["dark"],
            "color_info": COLORS["info"]["dark"],
            "color_background": COLORS["background"]["dark"],
            "color_surface": COLORS["surface"]["dark"],
            "color_text": COLORS["text"]["dark"],
            "color_text_secondary": COLORS["text_secondary"]["dark"],
        }
    else:  # light mode
        return {
            "color_primary": COLORS["primary"]["light"],
            "color_secondary": COLORS["secondary"]["light"],
            "color_accent": COLORS["accent"]["light"],
            "color_warning": COLORS["warning"]["light"],
            "color_danger": COLORS["danger"]["light"],
            "color_info": COLORS["info"]["light"],
            "color_background": COLORS["background"]["light"],
            "color_surface": COLORS["surface"]["light"],
            "color_text": COLORS["text"]["light"],
            "color_text_secondary": COLORS["text_secondary"]["light"],
        }