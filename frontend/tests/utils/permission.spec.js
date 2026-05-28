import { describe, it, expect } from 'vitest'
import { hasPermission, canEdit, canDelete, canCreate, canManageUsers } from '../../src/utils/permission'

describe('Permission Utils', () => {
  describe('hasPermission', () => {
    it('should return true for admin with CREATE permission', () => {
      expect(hasPermission('admin', 'create')).toBe(true)
    })

    it('should return true for admin with EDIT permission', () => {
      expect(hasPermission('admin', 'edit')).toBe(true)
    })

    it('should return true for admin with DELETE permission', () => {
      expect(hasPermission('admin', 'delete')).toBe(true)
    })

    it('should return true for admin with VIEW permission', () => {
      expect(hasPermission('admin', 'view')).toBe(true)
    })

    it('should return true for tester with CREATE permission', () => {
      expect(hasPermission('tester', 'create')).toBe(true)
    })

    it('should return true for tester with EDIT permission', () => {
      expect(hasPermission('tester', 'edit')).toBe(true)
    })

    it('should return false for tester with DELETE permission', () => {
      expect(hasPermission('tester', 'delete')).toBe(false)
    })

    it('should return true for tester with VIEW permission', () => {
      expect(hasPermission('tester', 'view')).toBe(true)
    })

    it('should return false for viewer with CREATE permission', () => {
      expect(hasPermission('viewer', 'create')).toBe(false)
    })

    it('should return false for viewer with EDIT permission', () => {
      expect(hasPermission('viewer', 'edit')).toBe(false)
    })

    it('should return false for viewer with DELETE permission', () => {
      expect(hasPermission('viewer', 'delete')).toBe(false)
    })

    it('should return true for viewer with VIEW permission', () => {
      expect(hasPermission('viewer', 'view')).toBe(true)
    })

    it('should return false for unknown role', () => {
      expect(hasPermission('unknown', 'view')).toBe(false)
    })

    it('should return false for empty role', () => {
      expect(hasPermission('', 'view')).toBe(false)
      expect(hasPermission(null, 'view')).toBe(false)
      expect(hasPermission(undefined, 'view')).toBe(false)
    })

    it('should return false for unknown permission', () => {
      expect(hasPermission('admin', 'unknown')).toBe(false)
    })
  })

  describe('canEdit', () => {
    it('should return true for admin', () => {
      expect(canEdit('admin')).toBe(true)
    })

    it('should return true for tester', () => {
      expect(canEdit('tester')).toBe(true)
    })

    it('should return false for viewer', () => {
      expect(canEdit('viewer')).toBe(false)
    })
  })

  describe('canDelete', () => {
    it('should return true for admin', () => {
      expect(canDelete('admin')).toBe(true)
    })

    it('should return false for tester', () => {
      expect(canDelete('tester')).toBe(false)
    })

    it('should return false for viewer', () => {
      expect(canDelete('viewer')).toBe(false)
    })
  })

  describe('canCreate', () => {
    it('should return true for admin', () => {
      expect(canCreate('admin')).toBe(true)
    })

    it('should return true for tester', () => {
      expect(canCreate('tester')).toBe(true)
    })

    it('should return false for viewer', () => {
      expect(canCreate('viewer')).toBe(false)
    })
  })

  describe('canManageUsers', () => {
    it('should return true for admin', () => {
      expect(canManageUsers('admin')).toBe(true)
    })

    it('should return false for tester', () => {
      expect(canManageUsers('tester')).toBe(false)
    })

    it('should return false for viewer', () => {
      expect(canManageUsers('viewer')).toBe(false)
    })
  })
})