import { Calendar, Home, User, Euro, FileText, Info, CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { LeaseExtraction } from '@/types/api';

interface ExtractionResultsProps {
  data: LeaseExtraction;
}

interface TableField {
  label: string;
  value: string;
  icon: React.ReactNode;
  highlight?: boolean;
  badge?: boolean;
  badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline';
}

export function ExtractionResults({ data }: ExtractionResultsProps) {
  const formatDate = (date: string | null | undefined) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('de-DE');
  };

  const formatCurrency = (amount: string | null | undefined) => {
    if (!amount) return '-';
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return '-';
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

  const active = isContractActive();

  const tableData: { category: string; fields: TableField[] }[] = [
    {
      category: 'Tenant Information',
      fields: [
        { 
          label: 'Tenant Name(s)', 
          value: data.tenants.map(t => `${t.first_name} ${t.last_name}`).join(', '),
          icon: <User className="h-4 w-4" />
        },
        { 
          label: 'Date(s) of Birth', 
          value: data.tenants.map(t => formatDate(t.birth_date)).join(', '),
          icon: <Calendar className="h-4 w-4" />
        },
      ]
    },
    {
      category: 'Property Details',
      fields: [
        { 
          label: 'Address', 
          value: `${data.address.street}, ${data.address.zip_code} ${data.address.city}`,
          icon: <Home className="h-4 w-4" />
        },
        { 
          label: 'Apartment Unit', 
          value: data.address.apartment_unit || '-',
          icon: <Home className="h-4 w-4" />
        },
        { 
          label: 'Square Meters', 
          value: data.square_meters || '-',
          icon: <Info className="h-4 w-4" />
        },
        { 
          label: 'Number of Rooms', 
          value: data.number_of_rooms || '-',
          icon: <Info className="h-4 w-4" />
        },
      ]
    },
    {
      category: 'Financial Details',
      fields: [
        { 
          label: 'Warm Rent (Total)', 
          value: formatCurrency(data.warm_rent),
          icon: <Euro className="h-4 w-4" />,
          highlight: true
        },
        { 
          label: 'Cold Rent (Base)', 
          value: formatCurrency(data.cold_rent),
          icon: <Euro className="h-4 w-4" />
        },
        { 
          label: 'Utilities (Nebenkosten)', 
          value: formatCurrency(data.utilities_cost),
          icon: <Euro className="h-4 w-4" />
        },
        { 
          label: 'Parking Fee', 
          value: formatCurrency(data.parking_rent),
          icon: <Euro className="h-4 w-4" />
        },
        { 
          label: 'Security Deposit', 
          value: formatCurrency(data.deposit_amount),
          icon: <Euro className="h-4 w-4" />
        },
      ]
    },
    {
      category: 'Contract Terms',
      fields: [
        { 
          label: 'Start Date', 
          value: formatDate(data.contract_start_date),
          icon: <Calendar className="h-4 w-4" />
        },
        { 
          label: 'End Date', 
          value: data.contract_end_date ? formatDate(data.contract_end_date) : 'Indefinite',
          icon: <Calendar className="h-4 w-4" />
        },
        { 
          label: 'Contract Status', 
          value: active ? 'Active' : 'Inactive',
          icon: active ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : <XCircle className="h-4 w-4 text-gray-400" />,
          badge: true,
          badgeVariant: active ? 'default' : 'secondary'
        },
        { 
          label: 'Notice Period', 
          value: data.notice_period || '-',
          icon: <Calendar className="h-4 w-4" />
        },
        { 
          label: 'Rent Increase Type', 
          value: data.rent_increase_type || '-',
          icon: <Info className="h-4 w-4" />
        },
      ]
    },
    {
      category: 'Landlord Information',
      fields: [
        { 
          label: 'Landlord Name', 
          value: data.landlord_name || '-',
          icon: <User className="h-4 w-4" />
        },
        { 
          label: 'Landlord Address', 
          value: data.landlord_address || '-',
          icon: <Home className="h-4 w-4" />
        },
      ]
    },
  ];

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Lease Agreement - Extracted Data
        </CardTitle>
        <CardDescription>Complete extraction results from AI analysis</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {tableData.map((section, idx) => (
            <div key={idx} className="space-y-3">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide border-b pb-2">
                {section.category}
              </h3>
              <div className="grid gap-2">
                {section.fields.map((field, fieldIdx) => (
                  <div 
                    key={fieldIdx} 
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      field.highlight ? 'bg-primary/5 border-primary/20' : 'bg-muted/30'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-muted-foreground">
                        {field.icon}
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {field.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {field.badge ? (
                        <Badge variant={field.badgeVariant}>
                          {field.value}
                        </Badge>
                      ) : (
                        <span className={`text-sm ${field.highlight ? 'font-bold text-primary' : 'font-semibold'}`}>
                          {field.value}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {data.rent_increase_type === 'Staffelmiete' && data.rent_increase_schedule && data.rent_increase_schedule.length > 0 && (
            <div className="space-y-3 pt-4 border-t">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Rent Increase Schedule (Staffelmiete)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="text-left p-3 font-medium">Effective Date</th>
                      <th className="text-left p-3 font-medium">Increase Amount</th>
                      <th className="text-right p-3 font-medium">New Cold Rent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.rent_increase_schedule.map((increase, idx) => (
                      <tr key={idx} className="border-b hover:bg-muted/50">
                        <td className="p-3">{formatDate(increase.date)}</td>
                        <td className="p-3">{increase.increase}</td>
                        <td className="p-3 text-right font-semibold">{formatCurrency(increase.new_cold_rent)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {data.special_clauses && data.special_clauses.length > 0 && (
            <div className="space-y-3 pt-4 border-t">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Special Clauses
              </h3>
              <ul className="space-y-2">
                {data.special_clauses.map((clause, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-2 rounded bg-muted/30">
                    <Info className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                    <span className="text-sm">{clause}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
