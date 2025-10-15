export interface TenantInfo {
  first_name: string;
  last_name: string;
  birth_date: string | null;
}

export interface AddressData {
  street: string;
  house_number: string;
  zip_code: string;
  city: string;
  apartment_unit?: string | null;
}

export interface LeaseExtraction {
  tenants: TenantInfo[];
  address: AddressData;
  warm_rent: string;
  cold_rent: string;
  utilities_cost?: string | null;
  parking_rent?: string | null;
  rent_increase_type: string;
  rent_increase_schedule?: Array<{
    date: string;
    increase: string;
    new_cold_rent: string;
  }> | null;
  contract_start_date: string;
  contract_end_date?: string | null;
  is_active: boolean;
  landlord_name?: string | null;
  landlord_address?: string | null;
  deposit_amount?: string | null;
  notice_period?: string | null;
  special_clauses?: string[] | null;
  utilities_included?: string[] | null;
  square_meters?: string | null;
  number_of_rooms?: string | null;
  confidence_scores: Record<string, number>;
  extraction_timestamp: string;
  ai_model_used: string;
}

export interface QualityMetrics {
  overall_score: number;
  confidence_score: number;
  completeness_score: number;
  validation_score: number;
  consistency_score: number;
  validation_errors: string[];
  warnings: string[];
  field_scores: Record<string, number>;
  quality_tier?: string;
}

export interface UploadResponse {
  success: boolean;
  extraction_id: string;
  file_path: string;
  extraction: LeaseExtraction;
  quality_metrics: QualityMetrics;
  processing_time_seconds: number;
}

export interface BatchUploadResult extends UploadResponse {
  file_index: number;
  original_filename: string;
}

export interface BatchUploadError {
  success: false;
  file_index: number;
  original_filename: string;
  error: string;
  error_type: string;
  status_code?: number;
}

export interface BatchUploadResponse {
  request_id: string;
  total_files: number;
  successful: number;
  failed: number;
  results: BatchUploadResult[];
  errors: BatchUploadError[] | null;
}

export interface ErrorResponse {
  success: false;
  error: string;
  error_type: string;
  details?: Record<string, unknown>;
}
