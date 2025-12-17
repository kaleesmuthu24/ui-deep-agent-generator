import { http } from './http';
export async function ping(){ return http.request('GET','/health'); }
