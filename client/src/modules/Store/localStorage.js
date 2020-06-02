import {writable as internal, get} from 'svelte/store'

// wraps a regular writable store
export default function writable(key, initialValue) {  
  // create an underlying store
  const store = internal(initialValue)
  const {subscribe, set} = store
  // get the last value from localStorage
  var json = null;
  if(typeof(window) != "undefined")
    json = localStorage.getItem(key);
  
  // use the value from localStorage if it exists
  if (json != null) {
    set(JSON.parse(json));
  }else{
    set(initialValue);
  }
  

  if(typeof(window) != "undefined" && localStorage.getItem(key) == null){
    localStorage.setItem(key, JSON.stringify(initialValue));
  }
  
  // return an object with the same interface as svelte's writable()
  return {
    // capture set and write to localStorage
    set(value) {
      if(typeof(window) != "undefined")
        localStorage.setItem(key, JSON.stringify(value))
        set(value)
    },
    setItem(keyTemp, value){
      if(typeof(window) != "undefined"){
        var temp = get(store);
        temp[keyTemp] = value
        this.set(temp);
        localStorage.setItem(key, JSON.stringify(temp))
      }
    },
    // capture updates and write to localStore
    update(cb) {
      const value = cb(get(store))
      this.set(value)
    },
    // punt subscriptions to underlying store
    subscribe,
    reset(){
      if(typeof(window) != "undefined")
        localStorage.setItem(key, JSON.stringify(initialValue));
        set(initialValue);
    },
    refresh(){
      if(typeof(window) != "undefined")
        set(JSON.parse(localStorage.getItem(key)));
    }
  }
}