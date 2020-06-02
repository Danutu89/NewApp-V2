import localStorage from './localStorage.js';

export const user = localStorage('user', {
                        auth: false,
                        name: '',
                        email: '',
                        avatar: '',
                        id: '',
                        real_name: '',
                        permissions: {},
                        theme: '',
                        theme_mode: ''
                    });

export default user;