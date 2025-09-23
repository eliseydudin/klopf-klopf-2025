export type StationEvent = {
  id: number
  timestamp: number
  station: string
  type: number
}

export type StationStats = {
  station: string
  branch: string
  event_amount: number
  today_events_amount: number
  amount_by_types: Record<string, number>
  events: [StationEvent]
}
