import { useState, useEffect, useCallback } from 'react';
import { useNotification } from '../contexts/NotificationContext';

/**
 * Custom hook for API calls with loading, error, and success states
 */
export const useApi = (apiFunction, options = {}) => {
  const {
    immediate = false,
    onSuccess = null,
    onError = null,
    showSuccessNotification = false,
    showErrorNotification = true,
    successMessage = 'Success!',
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const notification = useNotification();

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiFunction(...args);
        setData(result);

        if (showSuccessNotification) {
          notification.success(successMessage);
        }

        if (onSuccess) {
          onSuccess(result);
        }

        return result;
      } catch (err) {
        const errorMessage = err.message || 'An error occurred';
        setError(errorMessage);

        if (showErrorNotification) {
          notification.error(errorMessage);
        }

        if (onError) {
          onError(err);
        }

        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, onSuccess, onError, showSuccessNotification, showErrorNotification, successMessage, notification]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    data,
    loading,
    error,
    execute,
    setData,
  };
};

/**
 * Custom hook for fetching data on component mount
 */
export const useFetch = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  useEffect(() => {
    fetchData();
  }, dependencies);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
};

/**
 * Custom hook for mutations (POST, PUT, DELETE)
 */
export const useMutation = (apiFunction, options = {}) => {
  const {
    onSuccess = null,
    onError = null,
    showSuccessNotification = true,
    showErrorNotification = true,
    successMessage = 'Success!',
  } = options;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const notification = useNotification();

  const mutate = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiFunction(...args);

        if (showSuccessNotification) {
          notification.success(successMessage);
        }

        if (onSuccess) {
          onSuccess(result);
        }

        return result;
      } catch (err) {
        const errorMessage = err.message || 'An error occurred';
        setError(errorMessage);

        if (showErrorNotification) {
          notification.error(errorMessage);
        }

        if (onError) {
          onError(err);
        }

        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, onSuccess, onError, showSuccessNotification, showErrorNotification, successMessage, notification]
  );

  return {
    mutate,
    loading,
    error,
  };
};

/**
 * Custom hook for paginated data
 */
export const usePagination = (apiFunction, pageSize = 10) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchPage = useCallback(
    async (pageNum) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiFunction({ page: pageNum, page_size: pageSize });
        setData(result.items || result.data || result);
        setTotalPages(result.total_pages || 1);
        setTotalItems(result.total || result.items?.length || 0);
        setPage(pageNum);
      } catch (err) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, pageSize]
  );

  useEffect(() => {
    fetchPage(1);
  }, [fetchPage]);

  const nextPage = () => {
    if (page < totalPages) {
      fetchPage(page + 1);
    }
  };

  const prevPage = () => {
    if (page > 1) {
      fetchPage(page - 1);
    }
  };

  const goToPage = (pageNum) => {
    if (pageNum >= 1 && pageNum <= totalPages) {
      fetchPage(pageNum);
    }
  };

  return {
    data,
    loading,
    error,
    page,
    totalPages,
    totalItems,
    nextPage,
    prevPage,
    goToPage,
    refetch: () => fetchPage(page),
  };
};

