import os
import argparse

# ------------------------------------------------------------
# 1. Load a single text file
# ------------------------------------------------------------
def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# 2. Load all .txt files in the folder
# ------------------------------------------------------------
def load_all_text_files(folder):
    modules = {}
    for filename in os.listdir(folder):
        if filename.lower().endswith(".txt"):
            path = os.path.join(folder, filename)
            with open(path, "r", encoding="utf-8") as f:
                modules[filename] = f.read().strip()
    return modules


# ------------------------------------------------------------
# 3. Assemble prompt from a list of filenames
# ------------------------------------------------------------
def assemble_prompt(modules, order, debug=False):
    parts = []
    for name in order:
        if debug:
            print(f"[LOADING MODULE] {name}")
        if name not in modules:
            raise ValueError(f"Can't find this file,boss: {name}")
        parts.append(modules[name])
    return "\n\n".join(parts)


# ------------------------------------------------------------
# 4. Define assembly modes
# ------------------------------------------------------------
ASSEMBLY_MODES = {
    "full": [
        "ImageStyles.txt",
        "CharacterDetails.txt",
        "Poses.txt",
        "Backgrounds.txt",
        "EmotionPresets.txt",
        "Batching.txt"
    ],
    "style_only": [
        "ImageStyles.txt"
    ],
    "character_only": [
        "CharacterDetails.txt"
    ],
    "pose_background": [
        "Poses.txt",
        "Backgrounds.txt"
    ]
}



# ------------------------------------------------------------
# 5. CLI entry point
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Character Generator Prompt Engine"
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="full",
        choices=ASSEMBLY_MODES.keys(),
        help="Choose which prompt assembly mode to run"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: save the final prompt to a file"
    )

    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="List available assembly modes"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive terminal mode"
    )

    args = parser.parse_args()

    # List modes and exit
    if args.list_modes:
        print("Available modes:")
        for m in ASSEMBLY_MODES.keys():
            print(" -", m)
        return

    folder = "."
    modules = load_all_text_files(folder)

    # Interactive mode
    if args.interactive:
        interactive_mode(modules)
        return

    # Normal mode
    order = ASSEMBLY_MODES[args.mode]
    prompt = assemble_prompt(modules, order, debug=args.debug)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved prompt to {args.output}")
    else:
        print(prompt)


# ------------------------------------------------------------
# 6. Run the app
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
# ------------------------------------------------------------
# 7. Interactive terminal mode
# ------------------------------------------------------------
def interactive_mode(modules):
    config = load_config()
    presets = load_presets()

    while True:
        clear_screen()
        print_header("Interactive Mode")
        print_module_count(modules)

        # ----------------------------------------------------
        # Optional: show presets if they exist
        # ----------------------------------------------------
        if presets:
            print("\nPresets available (type 'p' to view):")

        available = list(modules.keys())
        for i, name in enumerate(available, start=1):
            print(f"{i}. {name}")

        print("\nSelect modules (comma numbers), 'p' for presets, or Enter to quit:")
        choice = input("> ").strip().lower()

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------
        if not choice:
            print("Exiting interactive mode.")
            return

        # ----------------------------------------------------
        # Show presets
        # ----------------------------------------------------
        if choice == "p":
            print_presets(presets)
            print("\nUse preset? Enter name or press Enter to cancel:")
            preset_name = input("> ").strip()
            if preset_name in presets:
                order = presets[preset_name]
                print_selection(order)
                prompt = assemble_prompt(modules, order, debug=False)
                print_header("Generated Prompt")
                print(prompt)
                append_history(order)
            if not ask_continue():
                return
            continue

        # ----------------------------------------------------
        # Normal numeric selection
        # ----------------------------------------------------
        try:
            raw_indices = [int(x) - 1 for x in choice.split(",")]
        except Exception:
            print("Invalid input.")
            if not ask_continue():
                return
            continue

        valid_indices = validate_selection(raw_indices, available)
        if not valid_indices:
            print("No valid selections.")
            if not ask_continue():
                return
            continue

        order = [available[i] for i in valid_indices]
        print_selection(order)

        # ----------------------------------------------------
        # Build prompt
        # ----------------------------------------------------
        prompt = assemble_prompt(modules, order, debug=False)
        print_header("Generated Prompt")
        print(prompt)

        # ----------------------------------------------------
        # Save to history
        # ----------------------------------------------------
        append_history(order)

        # ----------------------------------------------------
        # Save to file
        # ----------------------------------------------------
        print("\nSave to file? (y/n):")
        save = input("> ").strip().lower()

        if save == "y":
            print("Enter filename:")
            raw_name = input("> ").strip()
            filename = sanitize_filename(raw_name)

            if not filename:
                print("Invalid filename. Cancelled.")
            else:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(prompt)
                print(f"Saved to {filename}")

        # ----------------------------------------------------
        # Save as preset
        # ----------------------------------------------------
        print("\nSave this selection as a preset? (y/n):")
        save_preset = input("> ").strip().lower()

        if save_preset == "y":
            print("Preset name:")
            preset_name = input("> ").strip()
            if preset_name:
                presets[preset_name] = order
                save_presets(presets)
                print(f"Preset '{preset_name}' saved.")

        # ----------------------------------------------------
        # Continue?
        # ----------------------------------------------------
        if not ask_continue():
            return

# ------------------------------------------------------------
# 8. Basic input validation helpers
# ------------------------------------------------------------
def validate_selection(indices, available):
    valid = []
    for i in indices:
        if 0 <= i < len(available):
            valid.append(i)
        else:
            print(f"Skipping invalid selection: {i+1}")
    return valid
# ------------------------------------------------------------
# 9. Simple header helper
# ------------------------------------------------------------
def print_header(title):
    print("\n" + title)
    print("-" * len(title))
# ------------------------------------------------------------
# 10. Safe filename helper
# ------------------------------------------------------------
def sanitize_filename(name):
    name = name.strip()
    if not name:
        return None
    bad_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in bad_chars:
        name = name.replace(c, "_")
    return name
# ------------------------------------------------------------
# 11. Loop helper for interactive mode
# ------------------------------------------------------------
def ask_continue():
    print("\nGenerate another? (y/n):")
    ans = input("> ").strip().lower()
    return ans == "y"
# ------------------------------------------------------------
# 12. Clear-screen helper
# ------------------------------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
# ------------------------------------------------------------
# 13. Module count helper
# ------------------------------------------------------------
def print_module_count(modules):
    count = len(modules)
    print(f"\nLoaded {count} modules.")
# ------------------------------------------------------------
# 14. Selection summary helper
# ------------------------------------------------------------
def print_selection(order):
    print("\nSelected modules:")
    for name in order:
        print(f"- {name}")
# ------------------------------------------------------------
# 15. Configuration loader (optional defaults)
# ------------------------------------------------------------
import json

def load_config(path="config.json"):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config, path="config.json"):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        print("Could not save config.")


# ------------------------------------------------------------
# 16. Preset system (saved module combinations)
# ------------------------------------------------------------
def load_presets(path="presets.json"):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_presets(presets, path="presets.json"):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=2)
    except Exception:
        print("Could not save presets.")

def print_presets(presets):
    if not presets:
        print("\nNo presets saved.")
        return
    print("\nAvailable presets:")
    for name, items in presets.items():
        print(f"- {name}: {', '.join(items)}")


# ------------------------------------------------------------
# 17. History log (records past builds)
# ------------------------------------------------------------
def append_history(order, output_path="history.log"):
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(", ".join(order) + "\n")
    except Exception:
        print("Could not write to history log.")

def print_history(output_path="history.log"):
    if not os.path.exists(output_path):
        print("\nNo history yet.")
        return
    print("\nHistory:")
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            print("- " + line.strip())

