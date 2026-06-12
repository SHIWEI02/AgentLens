/**
 * 网络请求封装
 */

import fetch from '@system.fetch'

const API = {
  /**
   * 发送 GET 请求
   * @param {string} url - 请求地址
   * @param {Object} options - 配置选项
   * @returns {Promise}
   */
  get(url, options = {}) {
    return new Promise((resolve, reject) => {
      fetch.fetch({
        url: url,
        method: 'GET',
        responseType: options.responseType || 'json',
        success: (response) => {
          try {
            const data = typeof response.data === 'string'
              ? JSON.parse(response.data)
              : response.data
            resolve(data)
          } catch (e) {
            resolve(response.data)
          }
        },
        fail: (data, code) => {
          reject({ data, code })
        }
      })
    })
  },

  /**
   * 发送 POST 请求
   * @param {string} url - 请求地址
   * @param {Object} data - 请求数据
   * @param {Object} options - 配置选项
   * @returns {Promise}
   */
  post(url, data, options = {}) {
    return new Promise((resolve, reject) => {
      fetch.fetch({
        url: url,
        method: 'POST',
        data: typeof data === 'object' ? JSON.stringify(data) : data,
        header: {
          'Content-Type': 'application/json',
          ...options.header
        },
        responseType: options.responseType || 'json',
        success: (response) => {
          try {
            const resData = typeof response.data === 'string'
              ? JSON.parse(response.data)
              : response.data
            resolve(resData)
          } catch (e) {
            resolve(response.data)
          }
        },
        fail: (data, code) => {
          reject({ data, code })
        }
      })
    })
  },

  /**
   * 发送审批结果到 ntfy.sh
   * @param {string} server - ntfy 服务器地址
   * @param {string} topic - ntfy topic
   * @param {string} action - 审批动作 (approve/reject)
   * @param {string} requestId - 请求 ID
   * @returns {Promise}
   */
  sendApprovalResponse(server, topic, action, requestId) {
    const url = `${server}/${topic}`
    return this.post(url, {
      topic: topic,
      message: action,
      tags: [action],
      reply: requestId
    })
  },

  /**
   * 轮询 ntfy.sh 消息
   * @param {string} server - ntfy 服务器地址
   * @param {string} topic - ntfy topic
   * @param {string} since - 起始时间
   * @returns {Promise}
   */
  pollMessages(server, topic, since = '1m') {
    const url = `${server}/${topic}/json?poll=1&since=${since}`
    return this.get(url)
  }
}

export default API
