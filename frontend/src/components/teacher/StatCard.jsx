import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const StatCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend = null,
  trendLabel = '',
  color = 'blue' 
}) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  const trendColor = trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600';
  const trendIcon = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        {icon && (
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <span className="text-xl">{icon}</span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-gray-900">{value}</div>
        {subtitle && (
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        )}
        {trend !== null && (
          <div className={`flex items-center mt-2 text-sm ${trendColor}`}>
            <span className="mr-1">{trendIcon}</span>
            <span className="font-medium">{Math.abs(trend)}%</span>
            {trendLabel && <span className="ml-1 text-gray-500">{trendLabel}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StatCard;

