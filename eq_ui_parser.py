# eq_ui_parser.py

print("EQidle parser script started!") # This line confirms script execution

import xml.etree.ElementTree as ET
from eq_ui_model import *

# A mapping from XML tag names to our Python class names
# You will expand this mapping as you add more classes to eq_ui_model.py
EQ_ELEMENT_CLASSES = {
    "Screen": EQWindow, # SIDL.xml calls it 'Screen', we call it EQWindow
    "Button": EQButton,
    "Label": EQLabel,
    "Gauge": EQGauge,
    "StaticText": EQStaticText,
    "StaticAnimation": EQStaticAnimation,
    "InvSlot": EQInvSlot,
    # Add more as you define them in eq_ui_model.py
    # Example: "InvSlot": EQInvSlot, # You'd need to define EQInvSlot in eq_ui_model.py first
}
def parse_eq_ui_xml(xml_filepath):
    """
    Parses an EverQuest UI XML file and returns a list of parsed EQ UI objects.
    An EQ UI file can contain multiple top-level elements like Screen, Gauge, etc.
    """
    parsed_elements = []
    try:
        tree = ET.parse(xml_filepath)
        root = tree.getroot()
        print(f"DEBUG: Root element found: <{root.tag}>") # Debug line

        # The common root for EQ UI files is <XML>
        if root.tag == "XML":
            print(f"DEBUG: Root is <XML>. Iterating through its children.") # Debug line
            for xml_element in root:
                print(f"DEBUG: Child of <XML> root: <{xml_element.tag}>") # Debug line
                # Check if the child tag is one of our known EQ UI element types
                eq_class = EQ_ELEMENT_CLASSES.get(xml_element.tag)
                if eq_class:
                    eq_object = eq_class() # Create an instance of the corresponding class
                    parse_element_properties(xml_element, eq_object) # Parse its properties
                    parsed_elements.append(eq_object)
                else:
                    print(f"Warning: Unknown top-level element tag '{xml_element.tag}' in {xml_filepath}. Skipping.")
        elif root.tag in EQ_ELEMENT_CLASSES: # Handle cases where root might directly be a Screen or other element
            print(f"DEBUG: Root is a recognized UI element: <{root.tag}>") # Debug line
            eq_class = EQ_ELEMENT_CLASSES.get(root.tag)
            eq_object = eq_class()
            parse_element_properties(root, eq_object)
            parsed_elements.append(eq_object)
        else:
            print(f"Error: Unexpected root element '{root.tag}' in {xml_filepath}. Expected 'XML' or a defined UI element.")

        print(f"DEBUG: Finished parsing. Found {len(parsed_elements)} top-level elements.") # Debug line
        return parsed_elements

    except FileNotFoundError:
        print(f"Error: File not found: {xml_filepath}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML in {xml_filepath}: {e}")
        return []
    except Exception as e: # Broader catch for unexpected errors during parsing logic
        print(f"An unexpected error occurred during XML parsing: {e}")
        import traceback
        traceback.print_exc()
        return []
def parse_element_properties(xml_element, eq_object):
    """
    Recursively parses an XML element's attributes and child elements
    to populate the corresponding EQ object.
    """
    # 1. Handle direct attributes of the XML element (e.g., <Screen ID="MyWindowID">)
    for attr_name, attr_value in xml_element.attrib.items():
        if attr_name == "ID": # Special handling for the 'ID' attribute, which maps to screen_id
            eq_object.screen_id = attr_value
        elif attr_name == "name": # Sometimes 'name' is used for ScreenID or a descriptive name
            if hasattr(eq_object, 'screen_id') and eq_object.screen_id is None: # Only if ID wasn't already set
                eq_object.screen_id = attr_value
            # Also set 'item' if it matches the class hierarchy
            if hasattr(eq_object, 'item') and eq_object.item is None:
                eq_object.item = attr_value
        elif hasattr(eq_object, attr_name):
            # Attempt to convert value based on the default type of the attribute in the EQ object
            current_attr_value = getattr(eq_object, attr_name)
            if isinstance(current_attr_value, bool):
                setattr(eq_object, attr_name, attr_value.lower() == 'true')
            elif isinstance(current_attr_value, int):
                setattr(eq_object, attr_name, int(attr_value))
            elif isinstance(current_attr_value, float):
                setattr(eq_object, attr_name, float(attr_value))
            else:
                setattr(eq_object, attr_name, attr_value) # Default to string for others

    # 2. Handle child elements of the XML element
    for child_xml_element in xml_element:
        child_tag = child_xml_element.tag

        # Handle basic composite types (Point, Size, RGB) that are direct children with their own attributes/children
        if child_tag == "Location":
            if hasattr(eq_object, 'location') and isinstance(eq_object.location, EQPoint):
                # Check for X,Y as attributes first (less common for these tags, but possible)
                if 'X' in child_xml_element.attrib:
                    eq_object.location.x = int(child_xml_element.get("X"))
                if 'Y' in child_xml_element.attrib:
                    eq_object.location.y = int(child_xml_element.get("Y"))
                # Then check for X,Y as child elements (more common)
                for sub_child in child_xml_element:
                    if sub_child.tag == "X" and sub_child.text is not None:
                        eq_object.location.x = int(sub_child.text.strip())
                    elif sub_child.tag == "Y" and sub_child.text is not None:
                        eq_object.location.y = int(sub_child.text.strip())
        elif child_tag == "Size":
            if hasattr(eq_object, 'size') and isinstance(eq_object.size, EQSize):
                # Check for CX,CY as attributes first
                if 'CX' in child_xml_element.attrib:
                    eq_object.size.cx = int(child_xml_element.get("CX"))
                if 'CY' in child_xml_element.attrib:
                    eq_object.size.cy = int(child_xml_element.get("CY"))
                # Then check for CX,CY as child elements
                for sub_child in child_xml_element:
                    if sub_child.tag == "CX" and sub_child.text is not None:
                        eq_object.size.cx = int(sub_child.text.strip())
                    elif sub_child.tag == "CY" and sub_child.text is not None:
                        eq_object.size.cy = int(sub_child.text.strip())
        elif child_tag in ["TextColor", "BackgroundTextureTint", "DisabledColor", "MouseoverColor", "PressedColor", "FillTint", "LinesFillTint"]: # Handle all RGB types
            target_rgb_obj = None
            if child_tag == "TextColor" and hasattr(eq_object, 'text_color') and isinstance(eq_object.text_color, EQRGB):
                target_rgb_obj = eq_object.text_color
            elif child_tag == "BackgroundTextureTint" and hasattr(eq_object, 'background_texture_tint') and isinstance(eq_object.background_texture_tint, EQRGB):
                target_rgb_obj = eq_object.background_texture_tint
            elif child_tag == "DisabledColor" and hasattr(eq_object, 'disabled_color') and isinstance(eq_object.disabled_color, EQRGB):
                target_rgb_obj = eq_object.disabled_color
            elif child_tag == "MouseoverColor" and hasattr(eq_object, 'mouseover_color') and isinstance(eq_object.mouseover_color, EQRGB):
                target_rgb_obj = eq_object.mouseover_color
            elif child_tag == "PressedColor" and hasattr(eq_object, 'pressed_color') and isinstance(eq_object.pressed_color, EQRGB):
                target_rgb_obj = eq_object.pressed_color
            elif child_tag == "FillTint" and hasattr(eq_object, 'fill_tint') and isinstance(eq_object.fill_tint, EQRGB):
                target_rgb_obj = eq_object.fill_tint
            elif child_tag == "LinesFillTint" and hasattr(eq_object, 'lines_fill_tint') and isinstance(eq_object.lines_fill_tint, EQRGB):
                target_rgb_obj = eq_object.lines_fill_tint

            if target_rgb_obj:
                # Check for R,G,B,Alpha as attributes first
                if 'R' in child_xml_element.attrib: target_rgb_obj.r = int(child_xml_element.get("R"))
                if 'G' in child_xml_element.attrib: target_rgb_obj.g = int(child_xml_element.get("G"))
                if 'B' in child_xml_element.attrib: target_rgb_obj.b = int(child_xml_element.get("B"))
                if 'Alpha' in child_xml_element.attrib: target_rgb_obj.alpha = int(child_xml_element.get("Alpha"))
                # Then check for R,G,B,Alpha as child elements
                for sub_child in child_xml_element:
                    if sub_child.tag == "R" and sub_child.text is not None:
                        target_rgb_obj.r = int(sub_child.text.strip())
                    elif sub_child.tag == "G" and sub_child.text is not None:
                        target_rgb_obj.g = int(sub_child.text.strip())
                    elif sub_child.tag == "B" and sub_child.text is not None:
                        target_rgb_obj.b = int(sub_child.text.strip())
                    elif sub_child.tag == "Alpha" and sub_child.text is not None:
                        target_rgb_obj.alpha = int(sub_child.text.strip())
        elif child_tag == "DecalOffset": # Assuming DecalOffset is like Location
            if hasattr(eq_object, 'decal_offset') and isinstance(eq_object.decal_offset, EQPoint):
                if 'X' in child_xml_element.attrib: eq_object.decal_offset.x = int(child_xml_element.get("X"))
                if 'Y' in child_xml_element.attrib: eq_object.decal_offset.y = int(child_xml_element.get("Y"))
                for sub_child in child_xml_element:
                    if sub_child.tag == "X" and sub_child.text is not None:
                        eq_object.decal_offset.x = int(sub_child.text.strip())
                    elif sub_child.tag == "Y" and sub_child.text is not None:
                        eq_object.decal_offset.y = int(sub_child.text.strip())
        elif child_tag == "DecalSize": # Assuming DecalSize is like Size
            if hasattr(eq_object, 'decal_size') and isinstance(eq_object.decal_size, EQSize):
                if 'CX' in child_xml_element.attrib: eq_object.decal_size.cx = int(child_xml_element.get("CX"))
                if 'CY' in child_xml_element.attrib: eq_object.decal_size.cy = int(child_xml_element.get("CY"))
                for sub_child in child_xml_element:
                    if sub_child.tag == "CX" and sub_child.text is not None:
                        eq_object.decal_size.cx = int(sub_child.text.strip())
                    elif sub_child.tag == "CY" and sub_child.text is not None:
                        eq_object.decal_size.cy = int(sub_child.text.strip())
# Handle direct text content for elements like <Text>, <ScreenID>, <EQType>
        elif child_tag == "Text":
            if hasattr(eq_object, 'text'):
                eq_object.text = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "ScreenID":
            if hasattr(eq_object, 'screen_id'):
                eq_object.screen_id = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "EQType":
            if hasattr(eq_object, 'eq_type'):
                eq_object.eq_type = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "Font":
            if hasattr(eq_object, 'font') and child_xml_element.text is not None:
                try:
                    eq_object.font = int(child_xml_element.text.strip())
                except ValueError:
                    print(f"Warning: Could not convert Font value '{child_xml_element.text.strip()}' to int for {eq_object.screen_id}.")

        # Handle list of child pieces (e.g., <Pieces> inside a Window/Screen)
        elif child_tag == "Pieces":
            if hasattr(eq_object, "pieces") and isinstance(eq_object.pieces, list):
                for piece_element in child_xml_element:
                    piece_eq_class = EQ_ELEMENT_CLASSES.get(piece_element.tag)
                    if piece_eq_class:
                        piece_obj = piece_eq_class()
                        parse_element_properties(piece_element, piece_obj) # Recursive call
                        eq_object.pieces.append(piece_obj)
                    else:
                        print(f"Warning: Unrecognized child piece type '{piece_element.tag}' inside {xml_element.tag} (ID: {eq_object.screen_id}). Skipping.")
            else:
                print(f"Warning: '{type(eq_object).__name__}' object (ID: {eq_object.screen_id}) does not support 'Pieces' or 'pieces' attribute is not a list.")

        # Handle other simple direct properties that are children with text content
        elif child_xml_element.text is not None and child_xml_element.text.strip():
            prop_name = child_tag.lower()
            if hasattr(eq_object, prop_name):
                try:
                    current_attr = getattr(eq_object, prop_name)
                    if isinstance(current_attr, bool):
                        setattr(eq_object, prop_name, child_xml_element.text.strip().lower() == 'true')
                    elif isinstance(current_attr, int):
                        setattr(eq_object, prop_name, int(child_xml_element.text.strip()))
                    elif isinstance(current_attr, float):
                        setattr(eq_object, prop_name, float(child_xml_element.text.strip()))
                    else:
                        setattr(eq_object, prop_name, child_xml_element.text.strip())
                except (ValueError, AttributeError):
                    pass

def assemble_ui_hierarchy(parsed_elements):
    """
    Takes a flat list of parsed top-level UI elements and attempts to
    organize them into a hierarchical structure based on common EQ UI patterns.
    Returns a dictionary mapping top-level Window ScreenIDs to their objects,
    with child elements populated.
    """
    windows_by_id = {}
    all_elements_by_id = {}

    # First pass: Populate dictionaries for quick lookup
    for element in parsed_elements:
        if element.screen_id: # Only add if it has a ScreenID
            all_elements_by_id[element.screen_id] = element
        if isinstance(element, EQWindow):
            windows_by_id[element.screen_id] = element

    # Second pass: Assign children to windows and other parents
    for element_id, element_obj in all_elements_by_id.items():
        if not isinstance(element_obj, EQWindow): # Only process non-window elements
            # Try to find a parent Window based on ScreenID prefix
            # Example: 'IW_ReclaimButton' -> 'IW_' might point to 'InventoryWindow'
            # This is a common but not exhaustive pattern.
            for window_id, window_obj in windows_by_id.items():
                # Check for common prefix patterns for window IDs
                # E.g., InventoryWindow -> IW_Something, CharacterWindow -> CW_Something
                # Split 'Window' from the ID if it ends with 'Window' for prefix matching
                window_prefix = window_id
                if window_id.endswith("Window"):
                    window_prefix = window_id[:-6] # Remove 'Window'
                
                # Check if element_id starts with the window's prefix + '_'
                if window_prefix and element_id.startswith(window_prefix + '_'):
                    # If a match, add to parent's pieces list
                    window_obj.pieces.append(element_obj)
                    # Optionally, set a 'parent' attribute on the child for inverse lookup
                    element_obj.parent_id = window_obj.screen_id # Add parent_id attribute to ScreenPiece in eq_ui_model.py
                    break # Break after finding a parent to avoid adding to multiple windows


                # Additional check for common patterns like "EQUI_" related to main window
                # if element_id.startswith("EQUI_") and window_id == "MainUIWindow": # Example for a hypothetical MainUIWindow
                #     window_obj.pieces.append(element_obj)
                #     element_obj.parent_id = window_obj.screen_id
                #     break

            # Further logic here could look for explicit <Parent> tags/attributes
            # Or use spatial relationships for more complex cases.

    return windows_by_id, all_elements_by_id
if __name__ == "__main__":
    # Use EQUI_Inventory.xml as planned
    inventory_window_path = "F:/THJ/uifiles/default/EQUI_Inventory.xml" # Use your exact path here

    try:
        parsed_ui_elements = parse_eq_ui_xml(inventory_window_path)

        # --- NEW HIERARCHY ASSEMBLY LOGIC ---
        if parsed_ui_elements:
            print("\n--- Raw Parsed Top-Level Elements ---")
            # This section prints all elements found directly under the <XML> root
            for element in parsed_elements:
                print(element)

            print("\n--- Attempting UI Hierarchy Assembly ---")
            # Call the new assembly function to build the logical parent-child relationships
            main_windows, all_elements = assemble_ui_hierarchy(parsed_elements)

            print(f"\nFound {len(main_windows)} main window(s) with associated children:")
            # Iterate through the main windows that were identified and populate their children lists
            for window_id, window_obj in main_windows.items():
                print(f"Window: {window_obj}")
                if hasattr(window_obj, 'pieces') and window_obj.pieces: # Check if 'pieces' list is populated
                    print(f"  It contains {len(window_obj.pieces)} associated pieces:")
                    # Only print a few children for brevity, or add more logic to filter
                    for i, piece in enumerate(window_obj.pieces[:20]): # Print first 20 for example
                        print(f"    - {piece}")
                    if len(window_obj.pieces) > 20:
                        print("    ... and more associated children.")
                else:
                    print("  It has no directly associated pieces based on current prefix logic.")

        else:
            print("\nNo UI elements were parsed or an error occurred.")

    except Exception as e:
        print(f"\nAn unhandled error occurred during script execution: {e}")
        import traceback
        traceback.print_exc()
