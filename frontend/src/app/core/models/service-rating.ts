export interface ServiceRating {
  id: number;
  service_id: number;
  user_id: number;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceRatingSummary {
  service_id: number;
  average_rating: number;
  rating_count: number;
  user_rating: ServiceRating | null;
  comments: ServiceRating[];
}

export interface ServiceRatingPayload {
  user_id: number;
  rating: number;
  comment: string;
}
