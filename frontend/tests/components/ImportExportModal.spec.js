import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ImportExportModal from '../../src/components/ImportExportModal.vue'

describe('ImportExportModal', () => {
  it('should be defined', () => {
    const wrapper = mount(ImportExportModal, {
      props: {
        visible: false,
        type: 'export'
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should accept visible prop', () => {
    const wrapper = mount(ImportExportModal, {
      props: {
        visible: true,
        type: 'export'
      }
    })
    expect(wrapper.props('visible')).toBe(true)
  })

  it('should accept type prop', () => {
    const wrapper = mount(ImportExportModal, {
      props: {
        visible: false,
        type: 'import'
      }
    })
    expect(wrapper.props('type')).toBe('import')
  })

  it('should emit close event', async () => {
    const wrapper = mount(ImportExportModal, {
      props: {
        visible: true,
        type: 'export'
      }
    })
    wrapper.vm.handleCancel()
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should have correct title computed property', () => {
    const exportWrapper = mount(ImportExportModal, {
      props: {
        visible: false,
        type: 'export'
      }
    })
    expect(exportWrapper.vm.title).toBe('导出测试用例')

    const importWrapper = mount(ImportExportModal, {
      props: {
        visible: false,
        type: 'import'
      }
    })
    expect(importWrapper.vm.title).toBe('导入测试用例')
  })

  it('should watch visible prop', async () => {
    const wrapper = mount(ImportExportModal, {
      props: {
        visible: false,
        type: 'export'
      }
    })
    expect(wrapper.vm.isVisible).toBe(false)
    
    await wrapper.setProps({ visible: true })
    expect(wrapper.vm.isVisible).toBe(true)
  })
})