const os = require('os')
const path = require('path')
const fs = require('fs')
const { VvdManager, IVvdArchType, VelaImageType } = require('@aiot-toolkit/emulator')

const sdkHome = path.resolve(os.homedir(), '.vela')
const velaAvdCls = new VvdManager({ sdkHome })

async function createS5Emulator() {
  try {
    console.log('正在创建小米 Watch S5 模拟器...')

    // 获取默认镜像
    const defaultImage = VelaImageType.REL

    // 创建 VVD 配置
    velaAvdCls.createVvd({
      name: 'Xiaomi_Watch_S5',
      imageType: defaultImage,
      arch: IVvdArchType.arm,
      imageDir: path.join(sdkHome, 'sdk', 'system-images', 'vela-watch-5.0'),
      width: '480',
      height: '480'
    })

    // 修复配置文件 - 设置圆形屏幕参数
    const configPath = path.join(sdkHome, 'vvd', 'Xiaomi_Watch_S5.vvd', 'config.ini')
    if (fs.existsSync(configPath)) {
      let config = fs.readFileSync(configPath, 'utf-8')

      // 修复密度
      config = config.replace('hw.lcd.density=undefined', 'hw.lcd.density=320')

      // 修复形状
      config = config.replace('hw.lcd.shape=undefined', 'hw.lcd.shape=circle')

      // 修复设备类型
      config = config.replace('hw.device.flavor=undefined', 'hw.device.flavor=watch')

      // 修复圆角半径
      config = config.replace('ide.lcd.radius=undefined', 'ide.lcd.radius=240')

      // 修复镜像类型
      config = config.replace('ide.image.type=vela-release-4.0', 'ide.image.type=vela-watch-5.0')

      fs.writeFileSync(configPath, config, 'utf-8')
      console.log('✅ 已修复圆形屏幕配置')
    }

    console.log('✅ 小米 Watch S5 模拟器创建成功！')
    console.log('模拟器名称: Xiaomi_Watch_S5')
    console.log('分辨率: 480 × 480')
    console.log('屏幕形状: 圆形')
    console.log('')
    console.log('请在 AIoT IDE 中启动模拟器，然后运行 npm start 启动应用')

  } catch (error) {
    console.error('❌ 创建模拟器失败:', error.message)
    console.log('')
    console.log('如果模拟器已存在，请先删除后重新创建')
  }
}

createS5Emulator()
