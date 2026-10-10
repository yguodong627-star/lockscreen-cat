#!/usr/bin/env python3
"""手写生成 LockscreenCat.xcodeproj/project.pbxproj（不依赖 XcodeGen）。"""
import hashlib, os, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ios", "LockscreenCat"))
_seen = set()
def oid(name):
    h = hashlib.md5(name.encode()).hexdigest().upper()[:24]
    assert h not in _seen, name
    _seen.add(h); return h

def rel(p): return os.path.relpath(p, ROOT)
app_src = sorted(rel(p) for p in glob.glob(f"{ROOT}/App/*.swift"))
shared_src = sorted(rel(p) for p in glob.glob(f"{ROOT}/Shared/*.swift"))
widget_src = sorted(rel(p) for p in glob.glob(f"{ROOT}/Widget/*.swift"))
content_json = sorted(rel(p) for p in glob.glob(f"{ROOT}/Shared/Content/*.json"))  # 含 roasts_dog.json 等
# App 用 1024px 原图（Shared/Assets.xcassets）；小组件只带小图（Widget/WidgetAssets.xcassets，
# 由 tools/make_widget_assets.py 生成）——大图会让小组件超内存/归档失败，锁屏只剩灰色占位块。
app_resources = ["Shared/Assets.xcassets"] + content_json
widget_resources = ["Widget/WidgetAssets.xcassets"] + content_json
resources = ["Shared/Assets.xcassets", "Widget/WidgetAssets.xcassets"] + content_json
plain = ["App/Info.plist", "App/LockscreenCat.entitlements", "Widget/Info.plist",
         "Widget/LockscreenCatWidget.entitlements", "Config/Signing.xcconfig"]

def ftype(p):
    return {".swift": "sourcecode.swift", ".xcassets": "folder.assetcatalog", ".json": "text.json",
            ".plist": "text.plist.xml", ".entitlements": "text.plist.entitlements",
            ".xcconfig": "text.xcconfig"}[os.path.splitext(p)[1]]

files = app_src + shared_src + widget_src + resources + plain
FR = {f: oid("fileref:" + f) for f in files}
APP_PRODUCT, WIDGET_PRODUCT = oid("product:app"), oid("product:widget")
FW_WIDGETKIT, FW_SWIFTUI = oid("fw:WidgetKit"), oid("fw:SwiftUI")

o = []
def sec(name): o.append(f"\n/* Begin {name} section */")
def endsec(name): o.append(f"/* End {name} section */")

# build files
BF = {}
def bf(target, f): 
    k = (target, f); BF[k] = oid(f"buildfile:{target}:{f}"); return BF[k]
app_sources = [bf("app", f) for f in app_src + shared_src]
app_res = [bf("app", f) for f in app_resources]
w_sources = [bf("widget", f) for f in widget_src + shared_src]
w_res = [bf("widget", f) for f in widget_resources]
embed_bf = oid("buildfile:embed:widget")
w_fw = [oid("buildfile:widget:WidgetKit"), oid("buildfile:widget:SwiftUI")]

name = lambda f: os.path.basename(f)
sec("PBXBuildFile")
for (t, f), i in sorted(BF.items(), key=lambda x: x[1]):
    phase = "Resources" if f in resources else "Sources"
    o.append(f"\t\t{i} /* {name(f)} in {phase} */ = {{isa = PBXBuildFile; fileRef = {FR[f]} /* {name(f)} */; }};")
o.append(f"\t\t{embed_bf} /* LockscreenCatWidgetExtension.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = {WIDGET_PRODUCT} /* LockscreenCatWidgetExtension.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};")
o.append(f"\t\t{w_fw[0]} /* WidgetKit.framework in Frameworks */ = {{isa = PBXBuildFile; fileRef = {FW_WIDGETKIT} /* WidgetKit.framework */; }};")
o.append(f"\t\t{w_fw[1]} /* SwiftUI.framework in Frameworks */ = {{isa = PBXBuildFile; fileRef = {FW_SWIFTUI} /* SwiftUI.framework */; }};")
endsec("PBXBuildFile")

APP_T, W_T, PROJ = oid("target:app"), oid("target:widget"), oid("project")
PROXY, DEP = oid("proxy:widget"), oid("dep:widget")
sec("PBXContainerItemProxy")
o.append(f"""\t\t{PROXY} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = {PROJ} /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {W_T};
\t\t\tremoteInfo = LockscreenCatWidgetExtension;
\t\t}};""")
endsec("PBXContainerItemProxy")

EMBED = oid("phase:embed")
sec("PBXCopyFilesBuildPhase")
o.append(f"""\t\t{EMBED} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{embed_bf} /* LockscreenCatWidgetExtension.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};""")
endsec("PBXCopyFilesBuildPhase")

sec("PBXFileReference")
for f in files:
    o.append(f"\t\t{FR[f]} /* {name(f)} */ = {{isa = PBXFileReference; lastKnownFileType = {ftype(f)}; path = {name(f)}; sourceTree = \"<group>\"; }};")
o.append(f"\t\t{APP_PRODUCT} /* LockscreenCat.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = LockscreenCat.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
o.append(f"\t\t{WIDGET_PRODUCT} /* LockscreenCatWidgetExtension.appex */ = {{isa = PBXFileReference; explicitFileType = \"wrapper.app-extension\"; includeInIndex = 0; path = LockscreenCatWidgetExtension.appex; sourceTree = BUILT_PRODUCTS_DIR; }};")
o.append(f"\t\t{FW_WIDGETKIT} /* WidgetKit.framework */ = {{isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = WidgetKit.framework; path = System/Library/Frameworks/WidgetKit.framework; sourceTree = SDKROOT; }};")
o.append(f"\t\t{FW_SWIFTUI} /* SwiftUI.framework */ = {{isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = SwiftUI.framework; path = System/Library/Frameworks/SwiftUI.framework; sourceTree = SDKROOT; }};")
endsec("PBXFileReference")

APP_FW, W_FW = oid("phase:app:fw"), oid("phase:widget:fw")
sec("PBXFrameworksBuildPhase")
o.append(f"""\t\t{APP_FW} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{W_FW} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{w_fw[0]} /* WidgetKit.framework in Frameworks */,
\t\t\t\t{w_fw[1]} /* SwiftUI.framework in Frameworks */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};""")
endsec("PBXFrameworksBuildPhase")

# groups
G = {k: oid("group:" + k) for k in ["main", "App", "Widget", "Shared", "Content", "Config", "Products", "Frameworks"]}
def group(gid, label, children, path=None):
    ch = "\n".join(f"\t\t\t\t{c} /* {n} */," for c, n in children)
    p = f"\n\t\t\tpath = {path};" if path else ""
    nm = "" if path else (f"\n\t\t\tname = {label};" if label else "")
    o.append(f"""\t\t{gid}{f' /* {label} */' if label else ''} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
{ch}
\t\t\t);{nm}{p}
\t\t\tsourceTree = "<group>";
\t\t}};""")
sec("PBXGroup")
group(G["main"], None, [(G["App"], "App"), (G["Widget"], "Widget"), (G["Shared"], "Shared"), (G["Config"], "Config"),
                         (G["Frameworks"], "Frameworks"), (G["Products"], "Products")])
group(G["App"], "App", [(FR[f], name(f)) for f in app_src + ["App/Info.plist", "App/LockscreenCat.entitlements"]], "App")
group(G["Widget"], "Widget", [(FR[f], name(f)) for f in widget_src + ["Widget/WidgetAssets.xcassets", "Widget/Info.plist", "Widget/LockscreenCatWidget.entitlements"]], "Widget")
group(G["Shared"], "Shared", [(FR[f], name(f)) for f in shared_src + ["Shared/Assets.xcassets"]] + [(G["Content"], "Content")], "Shared")
group(G["Content"], "Content", [(FR[f], name(f)) for f in content_json], "Content")
group(G["Config"], "Config", [(FR["Config/Signing.xcconfig"], "Signing.xcconfig")], "Config")
group(G["Frameworks"], "Frameworks", [(FW_WIDGETKIT, "WidgetKit.framework"), (FW_SWIFTUI, "SwiftUI.framework")])
group(G["Products"], "Products", [(APP_PRODUCT, "LockscreenCat.app"), (WIDGET_PRODUCT, "LockscreenCatWidgetExtension.appex")])
endsec("PBXGroup")

APP_SRC, APP_RES, W_SRC, W_RES = oid("phase:app:src"), oid("phase:app:res"), oid("phase:w:src"), oid("phase:w:res")
CL = {k: oid("cl:" + k) for k in ["proj", "app", "widget"]}
CFG = {(t, c): oid(f"cfg:{t}:{c}") for t in ["proj", "app", "widget"] for c in ["Debug", "Release"]}

sec("PBXNativeTarget")
o.append(f"""\t\t{APP_T} /* LockscreenCat */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {CL['app']} /* Build configuration list for PBXNativeTarget "LockscreenCat" */;
\t\t\tbuildPhases = (
\t\t\t\t{APP_SRC} /* Sources */,
\t\t\t\t{APP_FW} /* Frameworks */,
\t\t\t\t{APP_RES} /* Resources */,
\t\t\t\t{EMBED} /* Embed Foundation Extensions */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t\t{DEP} /* PBXTargetDependency */,
\t\t\t);
\t\t\tname = LockscreenCat;
\t\t\tproductName = LockscreenCat;
\t\t\tproductReference = {APP_PRODUCT} /* LockscreenCat.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
\t\t{W_T} /* LockscreenCatWidgetExtension */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {CL['widget']} /* Build configuration list for PBXNativeTarget "LockscreenCatWidgetExtension" */;
\t\t\tbuildPhases = (
\t\t\t\t{W_SRC} /* Sources */,
\t\t\t\t{W_FW} /* Frameworks */,
\t\t\t\t{W_RES} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = LockscreenCatWidgetExtension;
\t\t\tproductName = LockscreenCatWidgetExtension;
\t\t\tproductReference = {WIDGET_PRODUCT} /* LockscreenCatWidgetExtension.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};""")
endsec("PBXNativeTarget")

sec("PBXProject")
o.append(f"""\t\t{PROJ} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1500;
\t\t\t\tLastUpgradeCheck = 1500;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{APP_T} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;
\t\t\t\t\t}};
\t\t\t\t\t{W_T} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;
\t\t\t\t\t}};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {CL['proj']} /* Build configuration list for PBXProject "LockscreenCat" */;
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = "zh-Hans";
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\ten,
\t\t\t\tBase,
\t\t\t\t"zh-Hans",
\t\t\t);
\t\t\tmainGroup = {G['main']};
\t\t\tproductRefGroup = {G['Products']} /* Products */;
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = (
\t\t\t\t{APP_T} /* LockscreenCat */,
\t\t\t\t{W_T} /* LockscreenCatWidgetExtension */,
\t\t\t);
\t\t}};""")
endsec("PBXProject")

def phase(pid, isa, label, ids, target):
    ch = "\n".join(f"\t\t\t\t{i} /* {name(f)} in {label} */," for (t, f), i in BF.items() if i in ids)
    o.append(f"""\t\t{pid} /* {label} */ = {{
\t\t\tisa = {isa};
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{ch}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};""")
sec("PBXResourcesBuildPhase")
phase(APP_RES, "PBXResourcesBuildPhase", "Resources", set(app_res), "app")
phase(W_RES, "PBXResourcesBuildPhase", "Resources", set(w_res), "widget")
endsec("PBXResourcesBuildPhase")
sec("PBXSourcesBuildPhase")
phase(APP_SRC, "PBXSourcesBuildPhase", "Sources", set(app_sources), "app")
phase(W_SRC, "PBXSourcesBuildPhase", "Sources", set(w_sources), "widget")
endsec("PBXSourcesBuildPhase")

sec("PBXTargetDependency")
o.append(f"""\t\t{DEP} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {W_T} /* LockscreenCatWidgetExtension */;
\t\t\ttargetProxy = {PROXY} /* PBXContainerItemProxy */;
\t\t}};""")
endsec("PBXTargetDependency")

def q(v):
    s = str(v)
    if s == "" : return '""'
    import re
    return s if re.fullmatch(r"[A-Za-z0-9_./]+", s) else '"' + s.replace('"', '\\"') + '"'
def settings(d):
    lines = []
    for k in sorted(d):
        v = d[k]
        if isinstance(v, list):
            lines.append(f"\t\t\t\t{k} = (\n" + "".join(f"\t\t\t\t\t{q(x)},\n" for x in v) + "\t\t\t\t);")
        else:
            lines.append(f"\t\t\t\t{k} = {q(v)};")
    return "\n".join(lines)

common = dict(ALWAYS_SEARCH_USER_PATHS="NO", ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS="YES",
    CLANG_ANALYZER_NONNULL="YES", CLANG_ENABLE_MODULES="YES", CLANG_ENABLE_OBJC_ARC="YES", COPY_PHASE_STRIP="NO",
    ENABLE_STRICT_OBJC_MSGSEND="YES", ENABLE_USER_SCRIPT_SANDBOXING="YES", GCC_C_LANGUAGE_STANDARD="gnu17",
    IPHONEOS_DEPLOYMENT_TARGET="17.0", LOCALIZATION_PREFERS_STRING_CATALOGS="YES", SDKROOT="iphoneos",
    SWIFT_VERSION="5.0", MTL_FAST_MATH="YES")
proj_dbg = dict(common, DEBUG_INFORMATION_FORMAT="dwarf", ENABLE_TESTABILITY="YES", GCC_OPTIMIZATION_LEVEL="0",
    GCC_PREPROCESSOR_DEFINITIONS=["DEBUG=1", "$(inherited)"], MTL_ENABLE_DEBUG_INFO="INCLUDE_SOURCE",
    ONLY_ACTIVE_ARCH="YES", SWIFT_ACTIVE_COMPILATION_CONDITIONS="DEBUG $(inherited)", SWIFT_OPTIMIZATION_LEVEL="-Onone")
proj_rel = dict(common, DEBUG_INFORMATION_FORMAT="dwarf-with-dsym", ENABLE_NS_ASSERTIONS="NO", MTL_ENABLE_DEBUG_INFO="NO",
    SWIFT_COMPILATION_MODE="wholemodule", VALIDATE_PRODUCT="YES")
app = dict(ASSETCATALOG_COMPILER_APPICON_NAME="AppIcon", ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME="AccentColor",
    CODE_SIGN_ENTITLEMENTS="App/LockscreenCat.entitlements", CODE_SIGN_STYLE="Automatic", CURRENT_PROJECT_VERSION="1",
    ENABLE_PREVIEWS="YES", GENERATE_INFOPLIST_FILE="NO", INFOPLIST_FILE="App/Info.plist",
    LD_RUNPATH_SEARCH_PATHS=["$(inherited)", "@executable_path/Frameworks"], MARKETING_VERSION="1.0",
    PRODUCT_BUNDLE_IDENTIFIER="$(BUNDLE_ID_PREFIX).lockscreencat", PRODUCT_NAME="$(TARGET_NAME)",
    SUPPORTED_PLATFORMS="iphoneos iphonesimulator", SUPPORTS_MACCATALYST="NO", SWIFT_EMIT_LOC_STRINGS="YES",
    TARGETED_DEVICE_FAMILY="1")
widget = dict(ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME="AccentColor",
    APPLICATION_EXTENSION_API_ONLY="YES",
    CODE_SIGN_ENTITLEMENTS="Widget/LockscreenCatWidget.entitlements", CODE_SIGN_STYLE="Automatic", CURRENT_PROJECT_VERSION="1",
    GENERATE_INFOPLIST_FILE="NO", INFOPLIST_FILE="Widget/Info.plist",
    LD_RUNPATH_SEARCH_PATHS=["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks"],
    MARKETING_VERSION="1.0", PRODUCT_BUNDLE_IDENTIFIER="$(BUNDLE_ID_PREFIX).lockscreencat.widget",
    PRODUCT_NAME="$(TARGET_NAME)", SKIP_INSTALL="YES", SUPPORTED_PLATFORMS="iphoneos iphonesimulator",
    SWIFT_EMIT_LOC_STRINGS="YES", TARGETED_DEVICE_FAMILY="1")
XC = FR["Config/Signing.xcconfig"]
sec("XCBuildConfiguration")
for (t, c), i in CFG.items():
    d = {"proj": proj_dbg if c == "Debug" else proj_rel, "app": app, "widget": widget}[t]
    base = f"\n\t\t\tbaseConfigurationReference = {XC} /* Signing.xcconfig */;" if t == "proj" else ""
    o.append(f"""\t\t{i} /* {c} */ = {{
\t\t\tisa = XCBuildConfiguration;{base}
\t\t\tbuildSettings = {{
{settings(d)}
\t\t\t}};
\t\t\tname = {c};
\t\t}};""")
endsec("XCBuildConfiguration")

sec("XCConfigurationList")
for t, label in [("proj", 'PBXProject "LockscreenCat"'), ("app", 'PBXNativeTarget "LockscreenCat"'),
                 ("widget", 'PBXNativeTarget "LockscreenCatWidgetExtension"')]:
    o.append(f"""\t\t{CL[t]} /* Build configuration list for {label} */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{CFG[(t,'Debug')]} /* Debug */,
\t\t\t\t{CFG[(t,'Release')]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};""")
endsec("XCConfigurationList")

out = "// !$*UTF8*$!\n{\n\tarchiveVersion = 1;\n\tclasses = {\n\t};\n\tobjectVersion = 56;\n\tobjects = {\n" + \
      "\n".join(o) + f"\n\t}};\n\trootObject = {PROJ} /* Project object */;\n}}\n"
d = os.path.join(ROOT, "LockscreenCat.xcodeproj")
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "project.pbxproj"), "w").write(out)
print("wrote", len(files), "files,", len(_seen), "ids")
