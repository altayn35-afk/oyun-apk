"""Keep the pinned p4a native recipes while using Android API 35 build tools.

Android's compatibility table requires AGP >=8.6 for API 35 and Gradle >=8.7
for AGP 8.6: https://developer.android.com/build/releases/agp-8-6-0-release-notes
This p4a hook runs after generation, before Gradle assembles the APK.
"""

from pathlib import Path
import re


def configure_gradle(directory):
    directory = Path(directory)
    gradle = directory / "build.gradle"
    wrapper = directory / "gradle/wrapper/gradle-wrapper.properties"
    build_text = gradle.read_text(encoding="utf8")
    wrapper_text = wrapper.read_text(encoding="utf8")
    build_text, count = re.subn(
        r"com\.android\.tools\.build:gradle:(?:8\.1\.1|8\.6\.0)(?=['\"])",
        "com.android.tools.build:gradle:8.6.0", build_text,
    )
    if count != 1:
        raise RuntimeError("Unexpected p4a Gradle template: Android plugin missing")
    build_text, count = re.subn(
        r"buildToolsVersion\s+['\"][^'\"]+['\"]",
        "buildToolsVersion '35.0.0'", build_text,
    )
    if count != 1:
        raise RuntimeError("Unexpected p4a Gradle template: build tools missing")
    wrapper_text, count = re.subn(
        r"gradle-(?:8\.0\.2|8\.7)-(?:all|bin)\.zip",
        "gradle-8.7-bin.zip", wrapper_text,
    )
    if count != 1:
        raise RuntimeError("Unexpected p4a Gradle wrapper version")
    gradle.write_text(build_text, encoding="utf8")
    wrapper.write_text(wrapper_text, encoding="utf8")


def before_apk_assemble(toolchain):
    configure_gradle(Path.cwd())
    configure_window_theme(Path.cwd())


def configure_window_theme(directory):
    """Preserve the existing non-fullscreen SDL layout for target API 35."""
    main = Path(directory) / "src/main"
    manifest = main / "AndroidManifest.xml"
    text = manifest.read_text(encoding="utf8")
    old = 'android:theme="@android:style/Theme.NoTitleBar"'
    new = 'android:theme="@style/ExplorerTheme"'
    if old not in text and new not in text:
        raise RuntimeError("Unexpected Android theme in generated manifest")
    text = text.replace(old, new)
    base = ('<resources><style name="ExplorerTheme" '
            'parent="android:style/Theme.NoTitleBar">{}</style></resources>\n')
    for qualifier, content in (
        ("values", ""),
        ("values-v35", '<item name="android:windowOptOutEdgeToEdgeEnforcement">true</item>'),
    ):
        folder = main / "res" / qualifier
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "explorer_theme.xml").write_text(base.format(content), encoding="utf8")
    manifest.write_text(text, encoding="utf8")
