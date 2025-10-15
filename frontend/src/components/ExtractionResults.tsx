import { Calendar, Home, User, Euro, FileText, Info } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { LeaseExtraction } from '@/types/api';

interface ExtractionResultsProps {
  data: LeaseExtraction;
}

export function ExtractionResults({ data }: ExtractionResultsProps) {
  const formatDate = (date: string | null) => {
    if (!date) return 'Not specified';
    return new Date(date).toLocaleDateString('de-DE');
  };

  const formatCurrency = (amount: string | null | undefined) => {
    if (!amount) return 'Not specified';
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return 'Not specified';
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(numAmount);
  };

  const isContractActive = () => {
    if (!data.contract_start_date) return false;
    const startDate = new Date(data.contract_start_date);
    const today = new Date();
    
    if (startDate > today) return false;
    
    if (data.contract_end_date) {
      const endDate = new Date(data.contract_end_date);
      return today <= endDate;
    }
    
    return true;
  };

  return (
    <div className="space-y-6">
      {/* Header with Contract Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Lease Agreement Details
              </CardTitle>
              <CardDescription>Extracted information from the document</CardDescription>
            </div>
            <Badge variant={isContractActive() ? "default" : "secondary"}>
              {isContractActive() ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Tenant Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-5 w-5 mr-2" />
            Tenant Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.tenants.map((tenant, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div>
                <p className="font-medium">{tenant.first_name} {tenant.last_name}</p>
                {tenant.birth_date && (
                  <p className="text-sm text-muted-foreground">
                    Born: {formatDate(tenant.birth_date)}
                  </p>
                )}
              </div>
              <Badge variant="outline">Tenant {idx + 1}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Property Address */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Home className="h-5 w-5 mr-2" />
            Property Address
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="font-medium">{data.address.street}</p>
            <p className="text-muted-foreground">
              {data.address.zip_code} {data.address.city}
            </p>
            {data.address.apartment_unit && (
              <div className="flex items-center mt-2">
                <Badge variant="secondary">Unit: {data.address.apartment_unit}</Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Rent Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Euro className="h-5 w-5 mr-2" />
            Rent Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Rent (Warm)</p>
              <p className="text-xl font-bold">{formatCurrency(data.warm_rent)}</p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Base Rent (Cold)</p>
              <p className="text-xl font-bold">{formatCurrency(data.cold_rent)}</p>
            </div>
          </div>

          {data.utilities_cost && (
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Utilities (Nebenkosten)</p>
              <p className="text-lg font-semibold">{formatCurrency(data.utilities_cost)}</p>
            </div>
          )}

          {data.parking_rent && (
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Parking Fee</p>
              <p className="text-lg font-semibold">{formatCurrency(data.parking_rent)}</p>
            </div>
          )}

          {/* Rent Increase Schedule */}
          {data.rent_increase_type === 'Staffelmiete' && data.rent_increase_schedule && data.rent_increase_schedule.length > 0 && (
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-3 flex items-center">
                <Info className="h-4 w-4 mr-2" />
                Rent Increase Schedule (Staffelmiete)
              </h4>
              <div className="space-y-2">
                {data.rent_increase_schedule.map((increase, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{formatDate(increase.date)}</span>
                    <span className="font-medium">{formatCurrency(increase.new_cold_rent)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Contract Dates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Contract Dates
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
            <span className="text-sm text-muted-foreground">Start Date</span>
            <span className="font-medium">{formatDate(data.contract_start_date)}</span>
          </div>
          {data.contract_end_date && (
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">End Date</span>
              <span className="font-medium">{formatDate(data.contract_end_date)}</span>
            </div>
          )}
          {!data.contract_end_date && (
            <Badge variant="outline" className="w-full justify-center py-2">
              Indefinite Contract
            </Badge>
          )}
        </CardContent>
      </Card>

      {/* Additional Information */}
      {(data.landlord_name || data.deposit_amount || data.notice_period || data.number_of_rooms) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Info className="h-5 w-5 mr-2" />
              Additional Information
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            {data.landlord_name && (
              <div className="p-3 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">Landlord</p>
                <p className="font-medium">{data.landlord_name}</p>
              </div>
            )}
            {data.deposit_amount !== null && (
              <div className="p-3 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">Security Deposit</p>
                <p className="font-medium">{formatCurrency(data.deposit_amount)}</p>
              </div>
            )}
            {data.notice_period && (
              <div className="p-3 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">Notice Period</p>
                <p className="font-medium">{data.notice_period}</p>
              </div>
            )}
            {data.number_of_rooms !== null && (
              <div className="p-3 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground">Rooms</p>
                <p className="font-medium">{data.number_of_rooms}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
