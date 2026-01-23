# Developing iOS Apps - 开发iOS应用

## 简介

Developing iOS Apps skill用于使用XcodeGen、SwiftUI和SPM构建、配置和部署iOS应用。

## 关键警告

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| "Library not loaded: @rpath/Framework" | XcodeGen不自动嵌入SPM动态框架 | **先在Xcode GUI中构建**（不是xcodebuild）。见故障排除 |
| `xcodegen generate`丢失签名 | 覆盖项目设置 | 在`project.yml`目标设置中配置，而不是全局 |
| 命令行签名失败 | 免费Apple ID限制 | 使用Xcode GUI或付费开发者账户（$99/年） |
| "Cannot be set when automaticallyAdjustsVideoMirroring is YES" | 在禁用自动调整的情况下设置`isVideoMirrored` | 先设置`automaticallyAdjustsVideoMirroring = false`。见相机/AVFoundation |

## 快速参考

| 任务 | 命令 |
|------|---------|
| 生成项目 | `xcodegen generate` |
| 构建模拟器 | `xcodebuild -destination 'platform=iOS Simulator,name=iPhone 17' build` |
| 构建设备（付费账户） | `xcodebuild -destination 'platform=iOS,name=DEVICE' -allowProvisioningUpdates build` |
| 清理DerivedData | `rm -rf ~/Library/Developer/Xcode/DerivedData/PROJECT-*` |
| 查找设备名称 | `xcrun xctrace list devices` |

## XcodeGen配置

### 最小project.yml

```yaml
name: AppName
options:
  bundleIdPrefix: com.company
  deploymentTarget:
    iOS: "16.0"

settings:
  base:
    SWIFT_VERSION: "6.0"

packages:
  SomePackage:
    url: https://github.com/org/repo
    from: "1.0.0"

targets:
  AppName:
    type: application
    platform: iOS
    sources:
      - path: AppName
    settings:
      base:
        INFOPLIST_FILE: AppName/Info.plist
        PRODUCT_BUNDLE_IDENTIFIER: com.company.appname
        CODE_SIGN_STYLE: Automatic
        DEVELOPMENT_TEAM: TEAM_ID_HERE
    dependencies:
      - package: SomePackage
```

### 代码签名配置

**个人（免费）账户：** 仅在Xcode GUI中工作。命令行构建需要付费账户。

```yaml
# 在目标设置中
settings:
  base:
    CODE_SIGN_STYLE: Automatic
    DEVELOPMENT_TEAM: TEAM_ID  # 从Xcode → Settings → Accounts获取
```

**获取Team ID：**
```bash
security find-identity -v -p codesigning | head -3
```

## iOS版本兼容性

### API版本更改

| iOS 17+仅限 | iOS 16兼容 |
|--------------|-------------------|
| `.onChange { old, new in }` | `.onChange { new in }` |
| `ContentUnavailableView` | 自定义VStack |
| `AVAudioApplication` | `AVAudioSession` |
| `@Observable`宏 | `@ObservableObject` |
| SwiftData | CoreData/Realm |

### 降低部署目标

1. 更新`project.yml`：
```yaml
deploymentTarget:
  iOS: "16.0"
```

2. 修复不兼容的API：
```swift
// iOS 17
.onChange(of: value) { oldValue, newValue in }

// iOS 16
.onChange(of: value) { newValue in }

// iOS 17
ContentUnavailableView("Title", systemImage: "icon")

// iOS 16
VStack {
    Image(systemName: "icon").font(.system(size: 48))
    Text("Title").font(.title2.bold())
}

// iOS 17
AVAudioApplication.shared.recordPermission

// iOS 16
AVAudioSession.sharedInstance().recordPermission
```

3. 重新生成：`xcodegen generate`

## 设备部署

### 首次设置

1. 通过USB连接设备
2. 在设备上信任计算机
3. 在Xcode中：Settings → Accounts → 添加Apple ID
4. 在scheme下拉列表中选择设备
5. 运行（`Cmd + R`）
6. 在设备上：Settings → General → VPN & Device Management → 信任

### 命令行构建（需要付费账户）

```bash
xcodebuild \
  -project App.xcodeproj \
  -scheme App \
  -destination 'platform=iOS,name=DeviceName' \
  -allowProvisioningUpdates \
  build
```

### 常见问题

| 错误 | 解决方案 |
|-------|----------|
| "Library not loaded: @rpath/Framework" | SPM动态框架未嵌入。先在Xcode GUI中构建，然后CLI工作 |
| "No Account for Team" | 在Xcode Settings → Accounts中添加Apple ID |
| "Provisioning profile not found" | 免费账户限制。使用Xcode GUI或获取付费账户 |
| Device not listed | 重新连接USB，在设备上信任计算机，重启Xcode |
| DerivedData won't delete | 先关闭Xcode：`pkill -9 Xcode && rm -rf ~/Library/Developer/Xcode/DerivedData/PROJECT-*` |

### 免费 vs 付费开发者账户

| 功能 | 免费Apple ID | 付费（$99/年） |
|---------|---------------|-----------------|
| Xcode GUI构建 | ✅ | ✅ |
| 命令行构建 | ❌ | ✅ |
| 应用有效性 | 7天 | 1年 |
| App Store | ❌ | ✅ |
| CI/CD | ❌ | ✅ |

## SPM依赖项

### SPM动态框架未嵌入

**根本原因：** XcodeGen不为SPM动态框架（如RealmSwift、Realm）生成"Embed Frameworks"构建阶段。应用成功构建但在启动时崩溃并显示：

```
dyld: Library not loaded: @rpath/RealmSwift.framework/RealmSwift
  Referenced from: /var/containers/Bundle/Application/.../App.app/App
  Reason: image not found
```

**为什么发生：**
- 静态框架（大多数SPM包）链接到二进制文件中 - 不需要嵌入
- 动态框架（RealmSwift等）必须复制到app bundle中
- XcodeGen为SPM包生成链接阶段但不生成嵌入阶段
- project.yml中的`embed: true`导致构建错误（XcodeGen限制）

**修复（手动，每个项目一次）：**
1. 在Xcode GUI中打开项目
2. 选择target → General → Frameworks, Libraries
3. 找到动态框架（RealmSwift）
4. 将"Do Not Embed"更改为"Embed & Sign"
5. 先从Xcode GUI构建和运行

**手动修复后：** 命令行构建（`xcodebuild`）将工作，因为Xcode在project.pbxproj中持久化嵌入设置。

**识别动态框架：**
```bash
# 检查框架是否为动态
file ~/Library/Developer/Xcode/DerivedData/PROJECT-*/Build/Products/Debug-iphoneos/FRAMEWORK.framework/FRAMEWORK
# 动态："Mach-O 64-bit dynamically linked shared library"
# 静态："current ar archive"
```

### 添加包

```yaml
packages:
  AudioKit:
    url: https://github.com/AudioKit/AudioKit
    from: "5.6.5"
  RealmSwift:
    url: https://github.com/realm/realm-swift
    from: "10.54.6"

targets:
  App:
    dependencies:
      - package: AudioKit
      - package: RealmSwift
        product: RealmSwift  # 当包有多个产品时的显式产品名称
```

### 解决依赖项（中国代理）

```bash
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082
xcodebuild -scmProvider system -resolvePackageDependencies
```

**从不清除全局SPM缓存**（`~/Library/Caches/org.swift.swiftpm`）。重新下载很慢。

## 相机/AVFoundation

相机预览需要真实设备（模拟器没有相机）。

### 快速调试检查表

1. **权限**：是否在Info.plist中添加了`NSCameraUsageDescription`？
2. **设备**：是否在真实设备上运行，而不是模拟器？
3. **会话运行**：是否在后台线程上调用了`session.startRunning()`？
4. **视图大小**：UIViewRepresentable是否具有非零边界？
5. **视频镜像**：在设置`isVideoMirrored`之前是否禁用了`automaticallyAdjustsVideoMirroring`？

### 视频镜像（前置相机）

**关键：** 在设置手动镜像之前必须禁用自动调整：

```swift
// 错误 - 在automaticallyAdjustsVideoMirroring为YES时崩溃
connection.isVideoMirrored = true

// 正确 - 先禁用自动调整
connection.automaticallyAdjustsVideoMirroring = false
connection.isVideoMirrored = true
```

### UIViewRepresentable大小问题

ZStack中的UIViewRepresentable可能具有零边界。使用显式frame修复：

```swift
// 坏：ZStack中的UIViewRepresentable可能获得零大小
ZStack {
    CameraPreviewView(session: session)  // 可能不可见！
    OtherContent()
}

// 好：显式大小
ZStack {
    GeometryReader { geo in
        CameraPreviewView(session: session)
            .frame(width: geo.size.width, height: geo.size.height)
    }
    .ignoresSafeArea()
    OtherContent()
}
```

### 调试日志模式

添加日志以跟踪相机流：

```swift
import os
private let logger = Logger(subsystem: "com.app", category: "Camera")

func start() async {
    logger.info("start() called, isRunning=\(self.isRunning)")
    // ... 设置代码 ...
    logger.info("session.startRunning() completed")
}

// 对于CGRect（不符合CustomStringConvertible）
logger.info("bounds=\(NSCoder.string(for: self.bounds))")
```

在Console.app中按子系统过滤。

**有关相机实现的详细信息：** 见[references/camera-avfoundation.md](references/camera-avfoundation.md)

## 资源

- [references/xcodegen-full.md](references/xcodegen-full.md) - 完整的project.yml选项
- [references/swiftui-compatibility.md](references/swiftui-compatibility.md) - iOS版本API差异
- [references/camera-avfoundation.md](references/camera-avfoundation.md) - 相机预览调试
- [references/testing-mainactor.md](references/testing-mainactor.md) - 测试@MainActor类（状态机、回归测试）
