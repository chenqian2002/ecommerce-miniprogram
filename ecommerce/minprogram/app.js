import { API_BASE_URL } from './utils/config';

App({
  onLaunch() {
    console.log('App launched');
  },

  globalData: {
    apiBaseUrl: API_BASE_URL
  }
});

