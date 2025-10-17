import React from 'react';
import { Button } from '../ui/button';

const EmptyState = ({
  icon = '📭',
  title = 'No data',
  description = '',
  action = null,
  actionLabel = '',
  onAction = null
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-gray-600 text-center max-w-md mb-6">{description}</p>
      )}
      {action || (onAction && actionLabel) ? (
        action || (
          <Button onClick={onAction}>
            {actionLabel}
          </Button>
        )
      ) : null}
    </div>
  );
};

export default EmptyState;

