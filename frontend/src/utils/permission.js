export function canEdit(role) {
  return role === "admin" || role === "tester";
}

export function canDelete(role) {
  return role === "admin";
}

export function canManageUsers(role) {
  return role === "admin";
}

export function canCreate(role) {
  return role === "admin" || role === "tester";
}

export const Permission = {
  EDIT: ["admin", "tester"],
  DELETE: ["admin"],
  MANAGE_USERS: ["admin"],
  CREATE: ["admin", "tester"],
  VIEW: ["admin", "tester", "viewer"]
};

export function hasPermission(role, permission) {
  if (!role) return false;
  const permissionRoles = Permission[permission?.toUpperCase()] || [];
  return permissionRoles.includes(role);
}