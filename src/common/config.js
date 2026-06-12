/**
 * 配置管理
 */

import storage from '@system.storage'

const CONFIG_KEYS = {
  NTFY_TOPIC: 'ntfy_topic',
  NTFY_SERVER: 'ntfy_server',
  APPROVE_TIMEOUT: 'approve_timeout',
  DANGEROUS_COMMANDS: 'dangerous_commands',
  PROTECTED_PATHS: 'protected_paths'
}

const DEFAULT_CONFIG = {
  ntfy_server: 'https://ntfy.sh',
  approve_timeout: '60',
  dangerous_commands: 'rm -rf,sudo,git push --force,docker rm,docker prune,terraform destroy,chmod 777',
  protected_paths: '.claude/hooks/,watch_approve.py,watch_done.py,watch.env'
}

const Config = {
  /**
   * 获取配置
   * @param {string} key - 配置键
   * @returns {Promise<string>}
   */
  get(key) {
    return new Promise((resolve, reject) => {
      storage.get({
        key: key,
        success: (data) => {
          resolve(data || DEFAULT_CONFIG[key] || '')
        },
        fail: (data, code) => {
          reject({ data, code })
        }
      })
    })
  },

  /**
   * 设置配置
   * @param {string} key - 配置键
   * @param {string} value - 配置值
   * @returns {Promise}
   */
  set(key, value) {
    return new Promise((resolve, reject) => {
      storage.set({
        key: key,
        value: value,
        success: () => {
          resolve()
        },
        fail: (data, code) => {
          reject({ data, code })
        }
      })
    })
  },

  /**
   * 获取所有配置
   * @returns {Promise<Object>}
   */
  async getAll() {
    const config = {}
    for (const key of Object.values(CONFIG_KEYS)) {
      try {
        config[key] = await this.get(key)
      } catch (e) {
        config[key] = DEFAULT_CONFIG[key] || ''
      }
    }
    return config
  },

  /**
   * 保存所有配置
   * @param {Object} config - 配置对象
   * @returns {Promise}
   */
  async saveAll(config) {
    for (const [key, value] of Object.entries(config)) {
      if (CONFIG_KEYS[key.toUpperCase()]) {
        await this.set(key, value)
      }
    }
  },

  /**
   * 检查配置是否完整
   * @returns {Promise<boolean>}
   */
  async isConfigured() {
    const topic = await this.get(CONFIG_KEYS.NTFY_TOPIC)
    return !!topic
  }
}

export default Config
export { CONFIG_KEYS, DEFAULT_CONFIG }
