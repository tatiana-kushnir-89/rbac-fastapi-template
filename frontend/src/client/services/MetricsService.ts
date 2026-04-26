/**
 * Metrics Service
 *
 * Note: This service should be auto-generated when running `npm run generate-client`.
 * This is a temporary implementation until the OpenAPI client is regenerated.
 */

import { OpenAPI } from "../core/OpenAPI"
import { request } from "../core/request"

export type Metrics = {
  total_users: number
  active_users: number
  total_items: number
  users_by_role: Record<string, number>
}

export class MetricsService {
  /**
   * Get Metrics
   * Get system metrics. Requires admin or manager role.
   */
  public static getMetrics(): Promise<Metrics> {
    return request(OpenAPI, {
      method: "GET",
      url: "/api/v1/metrics/",
    })
  }
}