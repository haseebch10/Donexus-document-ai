import * as XLSX from 'xlsx';
import type { BatchUploadResult, LeaseExtraction } from '@/types/api';

/**
 * Export a single lease extraction to JSON
 */
export const exportToJSON = (data: BatchUploadResult, filename?: string) => {
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `lease-extraction-${data.original_filename}-${new Date().toISOString()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

/**
 * Export multiple lease extractions to JSON
 */
export const exportAllToJSON = (results: BatchUploadResult[], filename?: string) => {
  const jsonStr = JSON.stringify(results, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `lease-extractions-all-${new Date().toISOString()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

/**
 * Convert lease extraction to a flat row for Excel
 */
const extractionToRow = (extraction: LeaseExtraction, result: BatchUploadResult) => {
  const tenantNames = extraction.tenants.map(t => `${t.first_name} ${t.last_name}`).join(', ');
  const tenantBirthDates = extraction.tenants.map(t => t.birth_date || 'N/A').join(', ');
  
  return {
    'File Name': result.original_filename,
    'Extraction ID': result.extraction_id,
    'Processing Time (s)': result.processing_time_seconds.toFixed(2),
    'Quality Score': (result.quality_metrics.overall_score).toFixed(1) + '%',
    'Quality Tier': result.quality_metrics.quality_tier || 'N/A',
    
    // Tenant Information
    'Tenant Name(s)': tenantNames,
    'Tenant Birth Date(s)': tenantBirthDates,
    
    // Address
    'Street': extraction.address.street,
    'House Number': extraction.address.house_number,
    'ZIP Code': extraction.address.zip_code,
    'City': extraction.address.city,
    'Apartment Unit': extraction.address.apartment_unit || 'N/A',
    
    // Financial
    'Warm Rent': extraction.warm_rent || 'N/A',
    'Cold Rent': extraction.cold_rent || 'N/A',
    'Utilities': extraction.utilities_cost || 'N/A',
    'Parking Rent': extraction.parking_rent || 'N/A',
    'Deposit': extraction.deposit_amount || 'N/A',
    
    // Contract
    'Start Date': extraction.contract_start_date || 'N/A',
    'End Date': extraction.contract_end_date || 'Indefinite',
    'Is Active': extraction.is_active ? 'Yes' : 'No',
    'Notice Period': extraction.notice_period || 'N/A',
    
    // Rent Increase
    'Rent Increase Type': extraction.rent_increase_type || 'N/A',
    
    // Property
    'Square Meters': extraction.square_meters || 'N/A',
    'Number of Rooms': extraction.number_of_rooms || 'N/A',
    
    // Landlord
    'Landlord Name': extraction.landlord_name || 'N/A',
    'Landlord Address': extraction.landlord_address || 'N/A',
    
    // Metadata
    'AI Model': extraction.ai_model_used,
    'Extraction Date': new Date(extraction.extraction_timestamp).toLocaleString('de-DE'),
    
    // Quality Metrics
    'Confidence': (result.quality_metrics.confidence_score * 100).toFixed(1) + '%',
    'Completeness': result.quality_metrics.completeness_score.toFixed(1) + '%',
    'Validation': result.quality_metrics.validation_score.toFixed(1) + '%',
    'Consistency': result.quality_metrics.consistency_score.toFixed(1) + '%',
  };
};

/**
 * Export a single lease extraction to Excel
 */
export const exportToExcel = (result: BatchUploadResult, filename?: string) => {
  const row = extractionToRow(result.extraction, result);
  
  const worksheet = XLSX.utils.json_to_sheet([row]);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Lease Extraction');
  
  // Auto-size columns
  const maxWidth = 50;
  const colWidths = Object.keys(row).map(key => ({
    wch: Math.min(Math.max(key.length, String(row[key as keyof typeof row]).length), maxWidth)
  }));
  worksheet['!cols'] = colWidths;
  
  const fileName = filename || `lease-extraction-${result.original_filename.replace('.pdf', '')}-${new Date().toISOString().split('T')[0]}.xlsx`;
  XLSX.writeFile(workbook, fileName);
};

/**
 * Export multiple lease extractions to Excel
 */
export const exportAllToExcel = (results: BatchUploadResult[], filename?: string) => {
  const rows = results.map(result => extractionToRow(result.extraction, result));
  
  const worksheet = XLSX.utils.json_to_sheet(rows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Lease Extractions');
  
  // Auto-size columns
  if (rows.length > 0) {
    const maxWidth = 50;
    const colWidths = Object.keys(rows[0]).map(key => ({
      wch: Math.min(
        Math.max(
          key.length,
          ...rows.map(row => String(row[key as keyof typeof row]).length)
        ),
        maxWidth
      )
    }));
    worksheet['!cols'] = colWidths;
  }
  
  const fileName = filename || `lease-extractions-all-${new Date().toISOString().split('T')[0]}.xlsx`;
  XLSX.writeFile(workbook, fileName);
};
