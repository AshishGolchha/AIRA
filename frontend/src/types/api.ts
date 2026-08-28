export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  request_id?: string;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorDetail;
  request_id?: string;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;
