export type Summary = {
  games: number;
  wins: number;
  draws: number;
  losses: number;
  score_percentage: number | null;
};

export type MonthlyTrend = Summary & { month: string };
export type OpeningSummary = Summary & { opening: string };
export type TimeClassSummary = Summary & { time_class: string };

export type Overview = Summary & {
  average_player_rating: number | null;
  average_opponent_rating: number | null;
  by_color: Record<"white" | "black", Summary>;
  by_time_class: TimeClassSummary[];
  monthly_trend: MonthlyTrend[];
  top_openings: OpeningSummary[];
};
