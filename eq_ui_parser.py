# eq_ui_parser.py

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
        # No explicit warning for unknown attributes here, as many attributes are set by child tags
        # or belong to properties of composite types (like Location.X)

    # 2. Handle child elements of the XML element
    for child_xml_element in xml_element:
        child_tag = child_xml_element.tag

        # Handle basic composite types (Point, Size, RGB) that are direct children
        # These composite types have their own children (X, Y, R, G, B, Alpha, CX, CY)
        if child_tag == "Location":
            if hasattr(eq_object, 'location') and isinstance(eq_object.location, EQPoint):
                for sub_child in child_xml_element:
                    if sub_child.tag == "X" and sub_child.text is not None:
                        eq_object.location.x = int(sub_child.text.strip())
                    elif sub_child.tag == "Y" and sub_child.text is not None:
                        eq_object.location.y = int(sub_child.text.strip())
        elif child_tag == "Size":
            if hasattr(eq_object, 'size') and isinstance(eq_object.size, EQSize):
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
                for sub_child in child_xml_element:
                    if sub_child.tag == "X" and sub_child.text is not None:
                        eq_object.decal_offset.x = int(sub_child.text.strip())
                    elif sub_child.tag == "Y" and sub_child.text is not None:
                        eq_object.decal_offset.y = int(sub_child.text.strip())
        elif child_tag == "DecalSize": # Assuming DecalSize is like Size
            if hasattr(eq_object, 'decal_size') and isinstance(eq_object.decal_size, EQSize):
                for sub_child in child_xml_element:
                    if sub_child.tag == "CX" and sub_child.text is not None:
                        eq_object.decal_size.cx = int(sub_child.text.strip())
                    elif sub_child.tag == "CY" and sub_child.text is not None:
                        eq_object.decal_size.cy = int(sub_child.text.strip())

        # Handle direct text content for elements like <Text>, <ScreenID>, <EQType>
        # These are child elements whose content is the value (e.g., <Text>My Label</Text>)
        elif child_tag == "Text":
            if hasattr(eq_object, 'text'):
                eq_object.text = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "ScreenID":
            if hasattr(eq_object, 'screen_id'):
                eq_object.screen_id = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "EQType":
            if hasattr(eq_object, 'eq_type'):
                eq_object.eq_type = child_xml_element.text.strip() if child_xml_element.text else ""
        elif child_tag == "Font": # Add Font as a direct property
            if hasattr(eq_object, 'font') and child_xml_element.text is not None:
                try:
                    eq_object.font = int(child_xml_element.text.strip())
                except ValueError:
                    print(f"Warning: Could not convert Font value '{child_xml_element.text.strip()}' to int for {eq_object.screen_id}.")


        # Handle list of child pieces (e.g., <Pieces> inside a Window/Screen)
        elif child_tag == "Pieces":
            if hasattr(eq_object, "pieces") and isinstance(eq_object.pieces, list):
                for piece_element in child_xml_element:
                    # Determine the type of the child piece and create the corresponding object
                    piece_eq_class = EQ_ELEMENT_CLASSES.get(piece_element.tag)
                    if piece_eq_class:
                        piece_obj = piece_eq_class()
                        parse_element_properties(piece_element, piece_obj) # Recursive call
                        eq_object.pieces.append(piece_obj)
                    else:
                        print(f"Warning: Unrecognized child piece type '{piece_element.tag}' inside {xml_element.tag} (ID: {eq_object.screen_id}). Skipping.")
            else:
                print(f"Warning: '{type(eq_object).__name__}' object (ID: {eq_object.screen_id}) does not support 'Pieces' or 'pieces' is not a list.")

        # Handle other simple direct properties that are children with text content
        # This is a fallback for simple properties not explicitly handled above
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
                    pass # Ignore if conversion or setting fails

if __name__ == "__main__":
    # Use EQUI_Inventory.xml as planned
    inventory_window_path = "F:/THJ/uifiles/default/EQUI_Inventory.xml" # Use your exact path here

    try: # Broad try-except to catch any unexpected errors during main execution
        parsed_ui_elements = parse_eq_ui_xml(inventory_window_path)

        if parsed_ui_elements:
            print(f"Successfully parsed {len(parsed_ui_elements)} top-level element(s) from {inventory_window_path}:")
            for element in parsed_ui_elements:
                print(element)
                if hasattr(element, 'pieces') and element.pieces:
                    print(f"  It contains {len(element.pieces)} child pieces:")
                    for i, piece in enumerate(element.pieces):
                        print(f"    Piece {i+1}: {piece}")
                else:
                    print(f"  It contains 0 child pieces or 'pieces' attribute is not a list.")
        else:
            print("No UI elements were parsed or an error occurred.")

    except Exception as e:
        print(f"An unhandled error occurred during script execution: {e}")
        import traceback
        traceback.print_exc()