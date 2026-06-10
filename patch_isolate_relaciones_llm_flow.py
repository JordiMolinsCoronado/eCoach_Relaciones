from pathlib import Path
import re

path = Path("eCoach_Relaciones.py")
text = path.read_text(encoding="utf-8")


def replace_async_function(source: str, name: str, replacement: str) -> str:
    pattern = (
        rf'\nasync def {re.escape(name)}\(.*?\):'
        rf'.*?(?=\nasync def |\ndef |\n# -{{5,}}|\Z)'
    )

    matches = list(re.finditer(pattern, source, flags=re.S))
    if not matches:
        raise SystemExit(f"Could not find async function: {name}")

    # Replace every duplicate definition, so no later copy can override it.
    for match in reversed(matches):
        source = (
            source[:match.start()]
            + "\n"
            + replacement.rstrip()
            + "\n"
            + source[match.end():]
        )

    print(f"Replaced {name}: {len(matches)} definition(s)")
    return source


# ---------------------------------------------------------------------
# 1) Disable inherited Patrimonio free-text control routing.
#
# Relationship initial messages are already handled before this function.
# Real-time activation messages have their own registered handler.
# Remaining free text should continue to the LLM orchestrator.
# ---------------------------------------------------------------------

control_replacement = r'''
async def try_handle_ecoach_control_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_text: str,
) -> bool:
    """Relaciones does not use inherited Patrimonio control branches."""
    return False
'''

text = replace_async_function(
    text,
    "try_handle_ecoach_control_message",
    control_replacement,
)


# ---------------------------------------------------------------------
# 2) Disable callbacks that belong to old fictitious paths.
# Keep only guided agency, real activation, free text and follow-up.
# ---------------------------------------------------------------------

disable_handlers = [
    "handle_alternatives_button",
    "handle_self_managed_path_button",
    "handle_delegated_path_button",
    "handle_design_mi_plan_button",
]

new_lines = []

for line in text.splitlines():
    stripped = line.strip()

    if (
        stripped.startswith("app.add_handler(")
        and any(handler in line for handler in disable_handlers)
    ):
        new_lines.append(
            "    # Disabled legacy Patrimonio/unused Relaciones route: "
            + stripped
        )
    else:
        new_lines.append(line)

text = "\n".join(new_lines) + "\n"

path.write_text(text, encoding="utf-8")
print("Disabled inherited Patrimonio control routing and unused callbacks.")
