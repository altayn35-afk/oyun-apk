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
    configure_rewarded_ads(Path.cwd())


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


def configure_rewarded_ads(directory):
    """Install test-only child-directed rewarded SDK into generated Android project."""
    directory = Path(directory)
    gradle = directory / "build.gradle"
    text = gradle.read_text(encoding="utf8")
    dependency = "implementation 'com.google.android.gms:play-services-ads:23.6.0'"
    # The p4a template uses a dependencies { } section for app dependencies.
    if dependency not in text:
        if "dependencies {" not in text:
            raise RuntimeError("Cannot locate Gradle dependencies block")
        idx = text.rfind("dependencies {")
        text = text[:idx] + "dependencies {\n    " + dependency + text[idx + len("dependencies {"):]
        gradle.write_text(text, encoding="utf8")

    manifest = directory / "src/main/AndroidManifest.xml"
    data = manifest.read_text(encoding="utf8")
    if 'com.google.android.gms.ads.APPLICATION_ID' not in data:
        marker = "</application>"
        if marker not in data:
            raise RuntimeError("Cannot locate Android application manifest section")
        entry = ('<meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" '
                 'android:value="ca-app-pub-1540771956171830~3252252740" />')
        data = data.replace(marker, entry + "\n" + marker, 1)
    if 'android.permission.INTERNET' not in data:
        data = data.replace('<application', '<uses-permission android:name="android.permission.INTERNET" />\n<application', 1)
    if 'android.permission.ACCESS_NETWORK_STATE' not in data:
        data = data.replace('<application', '<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n<application', 1)
    manifest.write_text(data, encoding="utf8")

    import shutil
    source = Path(__file__).with_name("RewardedBridge.java")
    dest = directory / "src/main/java/org/minikkasifler/ads/RewardedBridge.java"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
