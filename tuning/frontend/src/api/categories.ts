import axios from 'axios';
import { type IServiceCategory } from '../types';

// Указываем базовый URL нашего Django API
const API_URL = 'http://127.0.0.1:8000/api/v1/';

export const getServiceCategories = async (): Promise<IServiceCategory[]> => {
  const response = await axios.get(`${API_URL}service-categories/`);
  return response.data;
};