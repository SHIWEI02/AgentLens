/**
 * 工具函数
 */

const Utils = {
  /**
   * 格式化时间戳
   * @param {number} timestamp - 时间戳（秒）
   * @returns {string}
   */
  formatTime(timestamp) {
    const date = new Date(timestamp * 1000)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  },

  /**
   * 格式化相对时间
   * @param {number} timestamp - 时间戳（秒）
   * @returns {string}
   */
  formatRelativeTime(timestamp) {
    const now = Math.floor(Date.now() / 1000)
    const diff = now - timestamp

    if (diff < 60) {
      return '刚刚'
    } else if (diff < 3600) {
      return `${Math.floor(diff / 60)} 分钟前`
    } else if (diff < 86400) {
      return `${Math.floor(diff / 3600)} 小时前`
    } else {
      return `${Math.floor(diff / 86400)} 天前`
    }
  },

  /**
   * 截断字符串
   * @param {string} str - 原始字符串
   * @param {number} maxLength - 最大长度
   * @returns {string}
   */
  truncate(str, maxLength = 50) {
    if (!str || str.length <= maxLength) {
      return str
    }
    return str.substring(0, maxLength) + '...'
  },

  /**
   * 检查是否是危险命令
   * @param {string} command - 命令字符串
   * @param {string} dangerousCommands - 危险命令列表（逗号分隔）
   * @returns {boolean}
   */
  isDangerousCommand(command, dangerousCommands) {
    if (!command || !dangerousCommands) {
      return false
    }

    const patterns = dangerousCommands.split(',').map(p => p.trim())
    return patterns.some(pattern => command.includes(pattern))
  },

  /**
   * 检查是否涉及保护路径
   * @param {string} command - 命令字符串
   * @param {string} protectedPaths - 保护路径列表（逗号分隔）
   * @returns {Object} { isProtected: boolean, path: string | null }
   */
  checkProtectedPaths(command, protectedPaths) {
    if (!command || !protectedPaths) {
      return { isProtected: false, path: null }
    }

    const paths = protectedPaths.split(',').map(p => p.trim())
    for (const path of paths) {
      if (command.includes(path)) {
        return { isProtected: true, path }
      }
    }

    return { isProtected: false, path: null }
  },

  /**
   * 生成唯一 ID
   * @returns {string}
   */
  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  },

  /**
   * 延迟执行
   * @param {number} ms - 毫秒数
   * @returns {Promise}
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export default Utils
