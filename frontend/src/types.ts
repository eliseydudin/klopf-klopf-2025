export type StationEvent = {
  id: number
  timestamp: number
  station: string
  type: number
}

export type StationStats = {
  station: string
  branch: string
  today_events_amount: number
  amount_by_types: Record<string, number>
  latest_events: [StationEvent]
}
