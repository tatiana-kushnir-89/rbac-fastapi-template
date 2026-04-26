/**
 * Role-Based Access Control utilities for frontend
 */

export type UserRole = "admin" | "manager" | "member"

export const ROLES = {
  ADMIN: "admin" as const,
  MANAGER: "manager" as const,
  MEMBER: "member" as const,
}

/**
 * Check if user has one of the allowed roles
 */
export function hasRole(
  userRole: string | undefined,
  allowedRoles: UserRole | UserRole[]
): boolean {
  if (!userRole) return false
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles]
  return roles.includes(userRole as UserRole)
}

/**
 * Permission checks based on role
 */
export const permissions = {
  canListUsers: (role?: string) => hasRole(role, ["admin", "manager"]),
  canCreateUsers: (role?: string) => hasRole(role, "admin"),
  canUpdateAnyUser: (role?: string) => hasRole(role, "admin"),
  canDeleteUsers: (role?: string) => hasRole(role, "admin"),
  canViewMetrics: (role?: string) => hasRole(role, ["admin", "manager"]),
}

/**
 * Route guard helper - throws redirect if unauthorized
 */
export function requireRoles(
  userRole: string | undefined,
  allowedRoles: UserRole[]
): void {
  if (!hasRole(userRole, allowedRoles)) {
    throw new Error("Unauthorized")
  }
}