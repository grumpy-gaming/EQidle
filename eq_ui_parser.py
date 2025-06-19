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
    "TileLayoutBox": EQTilesLayoutBox,     # ADDED
    "Listbox": EQListBox,                  # ADDED
    "STMLbox": EQSTMLbox,                  # ADDED
    "VerticalLayoutBox": EQVerticalLayoutBox, # ADDED
    "Page": EQPage,                      # ADDED
    "TabBox": EQTabBox,                  # ADDED
    # Add more as you define them in eq_ui_model.py
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

        # Handle list of child pieces (e.g., <Pieces> inside a Window/Screen or Page)
        # These <Pieces> or <Pages> tags contain REFERENCES to other elements by their ScreenID,
        # typically in a "TAG:ID" format (e.g., <Pieces>Button:MyButtonID</Pieces>) or just the ID.
        elif child_tag == "Pieces": # Used by Screen, Page, LayoutBox, TileLayoutBox
            if hasattr(eq_object, "raw_pieces_references") and isinstance(eq_object.raw_pieces_references, list):
                # Check if the <Pieces> tag contains text (a ScreenID reference) or nested XML elements
                if child_xml_element.text and child_xml_element.text.strip():
                    # If it's a direct text reference (e.g., <Pieces>InvSlot23</Pieces>)
                    referenced_id = child_xml_element.text.strip()
                    eq_object.raw_pieces_references.append(referenced_id) # Store the ScreenID reference
                    print(f"DEBUG: Found direct piece reference '{referenced_id}' for {eq_object.screen_id}.")
                else:
                    # If it contains nested XML elements (e.g., <Pieces><Button>...</Button></Pieces>)
                    # Note: For EQ, <Pieces> usually contains REFERENCES, not nested full element definitions.
                    # This part might need to be removed/rethought if EQ's XML truly never nests full elements under <Pieces>
                    for piece_element in child_xml_element: # Loop through actual nested XML elements if they exist
                        piece_eq_class = EQ_ELEMENT_CLASSES.get(piece_element.tag)
                        if piece_eq_class:
                            piece_obj = piece_eq_class()
                            parse_element_properties(piece_element, piece_obj) # Recursive call
                            eq_object.pieces.append(piece_obj) # Add actual object
                            print(f"DEBUG: Found nested XML piece '{piece_obj.screen_id}' for {eq_object.screen_id}.")
                        else:
                            print(f"Warning: Unrecognized nested piece type '{piece_element.tag}' inside {xml_element.tag} (ID: {eq_object.screen_id}). Skipping.")
            else:
                print(f"Warning: '{type(eq_object).__name__}' object (ID: {eq_object.screen_id}) does not support 'raw_pieces_references' or 'raw_pieces_references' is not a list. Skipping piece: {child_xml_element.tag}.")
        elif child_tag == "Pages": # Used by TabBox
            if hasattr(eq_object, "raw_pages_references") and isinstance(eq_object.raw_pages_references, list):
                if child_xml_element.text and child_xml_element.text.strip():
                    referenced_id = child_xml_element.text.strip()
                    eq_object.raw_pages_references.append(referenced_id)
                    print(f"DEBUG: Found direct page reference '{referenced_id}' for {eq_object.screen_id}.")
                else:
                     for page_element in child_xml_element: # Loop through actual nested XML Page elements if they exist
                        page_eq_class = EQ_ELEMENT_CLASSES.get(page_element.tag)
                        if page_eq_class:
                            page_obj = page_eq_class()
                            parse_element_properties(page_element, page_obj) # Recursive call
                            eq_object.pages.append(page_obj) # Add actual object
                            print(f"DEBUG: Found nested XML page '{page_obj.screen_id}' for {eq_object.screen_id}.")
                        else:
                            print(f"Warning: Unrecognized nested page type '{page_element.tag}' inside {xml_element.tag} (ID: {eq_object.screen_id}). Skipping.")
            else:
                print(f"Warning: '{type(eq_object).__name__}' object (ID: {eq_object.screen_id}) does not support 'raw_pages_references' or 'raw_pages_references' is not a list. Skipping page: {child_xml_element.tag}.")


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
    Returns:
        - main_windows (dict): Mapping of Window ScreenIDs to their objects, with
          their 'pieces' and 'pages' lists populated with actual EQ objects.
        - all_elements (dict): Flat mapping of all element ScreenIDs to their objects.
        - unassigned_elements (list): Elements that could not be assigned to a parent.
    """
    windows_by_id = {}
    all_elements_by_id = {}
    unassigned_elements = []

    # First pass: Populate dictionaries for quick lookup
    # Also, identify all potential container elements (Windows, Pages, TabBoxes, LayoutBoxes)
    for element in parsed_elements:
        if element.screen_id: # Only add if it has a ScreenID
            all_elements_by_id[element.screen_id] = element
            if isinstance(element, EQWindow):
                windows_by_id[element.screen_id] = element
        # Important: Reset pieces/pages to empty lists if they contain string references from initial parsing
        # We want to populate them with actual objects here
        if hasattr(element, 'pieces') and all(isinstance(p, str) for p in element.pieces):
            # This check ensures we only clear and re-populate if they were raw string references
            # from the initial parse_element_properties step.
            element.raw_pieces_references = list(element.pieces) # Store a copy of raw references
            element.pieces = [] # Reset for actual objects
        if hasattr(element, 'pages') and all(isinstance(p, str) for p in element.pages):
            element.raw_pages_references = list(element.pages) # Store a copy of raw references
            element.pages = [] # Reset for actual objects


    # Second pass: Assign children to parents based on references
    # This pass will correctly populate 'pieces' and 'pages' lists with actual objects
    for element_id, element_obj in all_elements_by_id.items():
        # Handle elements that explicitly define children by reference (e.g., Window, Page, TabBox, LayoutBox)
        if hasattr(element_obj, 'raw_pieces_references') and element_obj.raw_pieces_references:
            for ref_str in element_obj.raw_pieces_references:
                # References can be like "InvSlot0" or "Screen:IW_CharacterView" or "TileLayoutBox:IW_Slots"
                ref_id = ref_str
                if ":" in ref_str:
                    parts = ref_str.split(":")
                    if len(parts) > 1: # Ensure there is an ID part
                        ref_id = parts[1] 

                child_obj = all_elements_by_id.get(ref_id)
                if child_obj:
                    element_obj.pieces.append(child_obj)
                    child_obj.parent_id = element_obj.screen_id
                else:
                    print(f"Warning: Could not find referenced child '{ref_str}' for parent '{element_id}'. Skipping.")
        
        if hasattr(element_obj, 'raw_pages_references') and element_obj.raw_pages_references:
            for ref_str in element_obj.raw_pages_references:
                ref_id = ref_str
                if ":" in ref_str:
                    parts = ref_str.split(":")
                    if len(parts) > 1:
                        ref_id = parts[1]

                child_obj = all_elements_by_id.get(ref_id)
                if child_obj:
                    element_obj.pages.append(child_obj)
                    child_obj.parent_id = element_obj.screen_id
                else:
                    print(f"Warning: Could not find referenced page '{ref_str}' for parent '{element_id}'. Skipping.")

    # Third pass: Assign remaining unassigned elements to the main InventoryWindow based on prefix (if applicable)
    # This is a fallback for elements not explicitly referenced in Pieces/Pages but belong to the main window
    main_inventory_window = windows_by_id.get("InventoryWindow") # Get the main window after its children were populated
    if main_inventory_window: # Only proceed if the main inventory window itself was parsed
        for element_id, element_obj in all_elements_by_id.items():
            # If element is not a Window/Page/TabBox/LayoutBox itself AND has no parent yet
            # And its ID starts with "IW_" (common for InventoryWindow children)
            if not isinstance(element_obj, (EQWindow, EQPage, EQTabBox, EQTilesLayoutBox, EQVerticalLayoutBox)) and \
               not element_obj.parent_id and \
               element_id.startswith("IW_"):
                
                # Check if it's already a direct child of a Page or LayoutBox within InventoryWindow
                # We need to be careful not to re-assign if it's already part of a sub-container
                is_already_child_of_subcontainer = False
                # Check direct pieces of main_inventory_window
                if hasattr(main_inventory_window, 'pieces'):
                    for piece in main_inventory_window.pieces:
                        if hasattr(piece, 'screen_id') and piece.screen_id == element_id:
                            is_already_child_of_subcontainer = True
                            break
                        # Also check pieces within nested containers like Pages and LayoutBoxes
                        if hasattr(piece, 'pieces') and any(hasattr(sub_piece, 'screen_id') and sub_piece.screen_id == element_id for sub_piece in piece.pieces):
                            is_already_child_of_subcontainer = True
                            break
                        if hasattr(piece, 'pages') and any(hasattr(page_in_piece, 'screen_id') and page_in_piece.screen_id == element_id for page_in_piece in piece.pages):
                            is_already_child_of_subcontainer = True
                            break
                # Check direct pages of main_inventory_window
                if hasattr(main_inventory_window, 'pages') and not is_already_child_of_subcontainer: # Only check if not already found
                    for page in main_inventory_window.pages:
                        if hasattr(page, 'screen_id') and page.screen_id == element_id:
                            is_already_child_of_subcontainer = True
                            break
                        if hasattr(page, 'pieces') and any(hasattr(piece_in_page, 'screen_id') and piece_in_page.screen_id == element_id for piece_in_page in page.pieces):
                            is_already_child_of_subcontainer = True
                            break
                        if hasattr(page, 'pages') and any(hasattr(page_in_page, 'screen_id') and page_in_page.screen_id == element_id for page_in_piece in page.pages):
                            is_already_child_of_subcontainer = True
                            break


                if not is_already_child_of_subcontainer:
                    main_inventory_window.pieces.append(element_obj)
                    element_obj.parent_id = main_inventory_window.screen_id

    # Fourth pass: Identify truly unassigned elements
    for element in parsed_elements:
        # An element is unassigned if it has no parent AND it's not a top-level container that we expect to be root (like InventoryWindow, Pages, TabBoxes, LayoutBoxes)
        if not element.parent_id and element.screen_id and \
           not isinstance(element, (EQWindow, EQPage, EQTabBox, EQTilesLayoutBox, EQVerticalLayoutBox)):
            unassigned_elements.append(element)

    return windows_by_id, all_elements_by_id, unassigned_elements


if __name__ == "__main__":
    # Use EQUI_Inventory.xml as planned
    # This path must be EXACTLY correct for your system!
    inventory_window_path = "F:/THJ/uifiles/default/EQUI_Inventory.xml" 

    try:
        # Step 1: Parse all elements as a flat list
        parsed_ui_elements = parse_eq_ui_xml(inventory_window_path)

        print("\n--- Raw Parsed Top-Level Elements (before assembly) ---")
        if parsed_ui_elements:
            for element in parsed_ui_elements: # Corrected from parsed_elements
                print(element)
        else:
            print("No top-level elements were parsed initially.")


        # Step 2: Assemble the logical hierarchy
        print("\n--- Attempting UI Hierarchy Assembly ---")
        main_windows, all_elements_map, unassigned_elements = assemble_ui_hierarchy(parsed_ui_elements)

        print(f"\nFound {len(main_windows)} identified main window(s):")
        if main_windows:
            for window_id, window_obj in main_windows.items():
                print(f"Window: {window_obj.screen_id}")
                # Print direct children for this window
                if hasattr(window_obj, 'pieces') and window_obj.pieces:
                    print(f"  Direct pieces ({len(window_obj.pieces)}):")
                    for i, piece in enumerate(window_obj.pieces[:20]): # Print first 20 pieces for brevity
                        print(f"    - {piece.screen_id} (Type: {type(piece).__name__}, Parent: {piece.parent_id})")
                    if len(window_obj.pieces) > 20: print("      ...")
                if hasattr(window_obj, 'pages') and window_obj.pages:
                    print(f"  Direct pages ({len(window_obj.pages)}):")
                    for i, page in enumerate(window_obj.pages[:5]): # Print first 5 pages for brevity
                        print(f"    - {page.screen_id} (Type: {type(page).__name__}, Parent: {page.parent_id})")
                    if len(window_obj.pages) > 5: print("      ...")
        else:
            print("No main windows were identified.")

        # Optionally, print unassigned elements
        if unassigned_elements:
            print(f"\n--- Unassigned Elements ({len(unassigned_elements)}) ---")
            for element in unassigned_elements[:10]: # Print first 10 unassigned elements
                print(f"  - {element.screen_id} (Type: {type(element).__name__})")
            if len(unassigned_elements) > 10: print("    ...")
        else:
            print("\nAll parsed elements were assigned to a parent or are top-level containers.")

    except Exception as e:
        print(f"\nAn unhandled error occurred during script execution: {e}")
        import traceback
        traceback.print_exc()
