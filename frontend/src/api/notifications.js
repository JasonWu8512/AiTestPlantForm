import request from './request'

export function getNotificationConfigs(params) {
  return request({
    url: '/notifications/configs/',
    method: 'get',
    params
  })
}

export function getNotificationConfig(id) {
  return request({
    url: `/notifications/configs/${id}/`,
    method: 'get'
  })
}

export function createNotificationConfig(data) {
  return request({
    url: '/notifications/configs/',
    method: 'post',
    data
  })
}

export function updateNotificationConfig(id, data) {
  return request({
    url: `/notifications/configs/${id}/`,
    method: 'put',
    data
  })
}

export function deleteNotificationConfig(id) {
  return request({
    url: `/notifications/configs/${id}/`,
    method: 'delete'
  })
}

export function testNotificationConfig(id) {
  return request({
    url: `/notifications/configs/${id}/test_send/`,
    method: 'post'
  })
}

export function getNotificationRecords(params) {
  return request({
    url: '/notifications/records/',
    method: 'get',
    params
  })
}

export function resendNotificationRecord(id) {
  return request({
    url: `/notifications/records/${id}/resend/`,
    method: 'post'
  })
}