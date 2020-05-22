import axios from 'axios';

export const instance = axios.create({
    headers: {
      common: {
        Token: ''
      }
    }
});