/**
 * WebSocket Client - ניהול חיבורי WebSocket ועדכון DOM
 */

class WebSocketClient {
    constructor(url, topics = []) {
        this.url = url;
        this.topics = topics;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // מילישניות
        this.isConnecting = false;
        this.messageHandlers = [];
        this.onConnectCallbacks = [];
        this.onDisconnectCallbacks = [];
    }

    /**
     * חיבור ל-WebSocket
     */
    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            console.log("WebSocket already connected or connecting");
            return;
        }

        this.isConnecting = true;
        
        try {
            const wsUrl = this.url.startsWith('ws://') || this.url.startsWith('wss://') 
                ? this.url 
                : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${this.url}`;
            
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                console.log("WebSocket connected");
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                
                // הרשמה ל-topics
                if (this.topics.length > 0) {
                    this.topics.forEach(topic => {
                        this.subscribe(topic);
                    });
                }
                
                // קריאה ל-callbacks
                this.onConnectCallbacks.forEach(callback => callback(event));
            };

            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (e) {
                    console.error("Error parsing WebSocket message:", e);
                }
            };

            this.ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                this.isConnecting = false;
            };

            this.ws.onclose = (event) => {
                console.log("WebSocket disconnected");
                this.isConnecting = false;
                this.ws = null;
                
                // קריאה ל-callbacks
                this.onDisconnectCallbacks.forEach(callback => callback(event));
                
                // ניסיון חיבור מחדש
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnect();
                } else {
                    console.error("Max reconnection attempts reached");
                }
            };

        } catch (error) {
            console.error("Error creating WebSocket:", error);
            this.isConnecting = false;
        }
    }

    /**
     * ניתוק מה-WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.reconnectAttempts = this.maxReconnectAttempts; // מניעת ניסיונות חיבור מחדש
    }

    /**
     * ניסיון חיבור מחדש עם exponential backoff
     */
    reconnect() {
        if (this.isConnecting) {
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * הרשמה ל-topic
     */
    subscribe(topic) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: "subscribe",
                topic: topic
            }));
            console.log(`Subscribed to topic: ${topic}`);
        } else {
            // הוספה לרשימה אם עדיין לא מחובר
            if (!this.topics.includes(topic)) {
                this.topics.push(topic);
            }
        }
    }

    /**
     * ביטול הרשמה ל-topic
     */
    unsubscribe(topic) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: "unsubscribe",
                topic: topic
            }));
            console.log(`Unsubscribed from topic: ${topic}`);
        }
        
        // הסרה מהרשימה
        this.topics = this.topics.filter(t => t !== topic);
    }

    /**
     * הוספת handler להודעות
     */
    onMessage(callback) {
        this.messageHandlers.push(callback);
    }

    /**
     * הוספת callback לחיבור
     */
    onConnect(callback) {
        this.onConnectCallbacks.push(callback);
    }

    /**
     * הוספת callback לניתוק
     */
    onDisconnect(callback) {
        this.onDisconnectCallbacks.push(callback);
    }

    /**
     * טיפול בהודעות
     */
    handleMessage(message) {
        // קריאה לכל ה-handlers
        this.messageHandlers.forEach(handler => {
            try {
                handler(message);
            } catch (e) {
                console.error("Error in message handler:", e);
            }
        });

        // עדכון DOM אוטומטי אם יש topic ו-data
        if (message.topic && message.data) {
            this.updateDOM(message.topic, message.data);
        }
    }

    /**
     * עדכון DOM לפי data attributes
     */
    updateDOM(topic, data) {
        // מציאת כל ה-elements עם data-ws-topic
        const elements = document.querySelectorAll(`[data-ws-topic="${topic}"]`);
        
        elements.forEach(element => {
            // עדכון כל ה-fields בתוך ה-element
            Object.keys(data).forEach(key => {
                // חיפוש בתוך ה-element
                const fieldElements = element.querySelectorAll(`[data-ws-field="${key}"]`);
                
                fieldElements.forEach(fieldElement => {
                    this.updateField(fieldElement, key, data[key]);
                });
                
                // חיפוש על ה-element עצמו (למקרה שה-data-ws-field על ה-element)
                if (element.hasAttribute('data-ws-field') && element.getAttribute('data-ws-field') === key) {
                    this.updateField(element, key, data[key]);
                }
                
                // עדכון CSS variable עבור cpu_temp_percent
                if (key === 'cpu_temp_percent') {
                    // חיפוש progress-bar עם data-ws-field או בתוך element
                    const progressBars = element.querySelectorAll('.progress-bar-temp');
                    progressBars.forEach(progressBar => {
                        if (progressBar.hasAttribute('data-ws-field') && progressBar.getAttribute('data-ws-field') === 'cpu_temp_percent') {
                            progressBar.style.setProperty('--temp-fill', `${data[key]}%`);
                        }
                    });
                    
                    // בדיקה אם ה-element עצמו הוא progress-bar
                    if (element.classList.contains('progress-bar-temp') && element.getAttribute('data-ws-field') === 'cpu_temp_percent') {
                        element.style.setProperty('--temp-fill', `${data[key]}%`);
                    }
                }
                
                // עדכון CSS variable עבור cpu_usage ו-ram_percent
                if (key === 'cpu_usage' || key === 'ram_percent') {
                    const progressBars = element.querySelectorAll(`.progress-bar[data-ws-field="${key}"]`);
                    progressBars.forEach(progressBar => {
                        progressBar.style.setProperty('--fill-percent', `${data[key]}%`);
                    });
                }
            });

            // עדכון classes
            const classElements = element.querySelectorAll(`[data-ws-field-class]`);
            classElements.forEach(classElement => {
                const fieldName = classElement.getAttribute('data-ws-field-class');
                if (data[fieldName]) {
                    this.updateClass(classElement, data[fieldName]);
                }
            });
            
            // בדיקה אם ה-element עצמו יש לו data-ws-field-class
            if (element.hasAttribute('data-ws-field-class')) {
                const fieldName = element.getAttribute('data-ws-field-class');
                if (data[fieldName]) {
                    this.updateClass(element, data[fieldName]);
                }
            }
        });
    }

    /**
     * עדכון field ספציפי
     */
    updateField(element, fieldName, value) {
        if (!element) return;

        // בדיקה אם זה progress bar fill
        if (element.classList.contains('progress-bar-fill')) {
            this.updateProgressBar(element, value);
            return;
        }

        // בדיקה אם זה progress-bar עם --temp-fill (טמפרטורה)
        if (element.hasAttribute('data-ws-field') && element.dataset.wsField === 'cpu_temp_percent') {
            // אם זה progress-bar עצמו, עדכן רק את ה-CSS variable
            if (element.classList.contains('progress-bar-temp')) {
                element.style.setProperty('--temp-fill', `${value}%`);
                return; // אל תעדכן כטקסט
            }
            // אם זה בתוך progress-bar, עדכן את ה-progress-bar
            const progressBar = element.closest('.progress-bar-temp');
            if (progressBar) {
                progressBar.style.setProperty('--temp-fill', `${value}%`);
            }
            return; // אל תעדכן כטקסט
        }

        // בדיקה אם זה progress-bar עם --fill-percent (CPU/RAM)
        if (element.hasAttribute('data-ws-field') && (element.dataset.wsField === 'cpu_usage' || element.dataset.wsField === 'ram_percent')) {
            // אם זה progress-bar עצמו, עדכן רק את ה-CSS variable
            if (element.classList.contains('progress-bar-cpu') || element.classList.contains('progress-bar-ram')) {
                element.style.setProperty('--fill-percent', `${value}%`);
                return; // אל תעדכן כטקסט
            }
            // אם זה בתוך progress-bar, עדכן את ה-progress-bar
            const progressBar = element.closest('.progress-bar-cpu, .progress-bar-ram');
            if (progressBar) {
                progressBar.style.setProperty('--fill-percent', `${value}%`);
            }
            return; // אל תעדכן כטקסט
        }

        // עדכון טקסט - עם פורמט מיוחד לטמפרטורה ו-CPU Usage
        if (fieldName === 'cpu_temp') {
            if (element.tagName === 'SPAN' || element.tagName === 'DIV' || element.tagName === 'P') {
                element.textContent = `${value}°C`;
            } else {
                element.value = value;
            }
        } else if (fieldName === 'cpu_usage') {
            // הוספת % ל-CPU Usage
            if (element.tagName === 'SPAN' || element.tagName === 'DIV' || element.tagName === 'P') {
                element.textContent = `${value}%`;
            } else {
                element.value = value;
            }
        } else {
            // עדכון טקסט רגיל
            if (element.tagName === 'SPAN' || element.tagName === 'DIV' || element.tagName === 'P') {
                element.textContent = value;
            } else {
                element.value = value;
            }
        }
    }

    /**
     * עדכון progress bar
     */
    updateProgressBar(element, value) {
        if (!element) return;
        
        // עדכון width
        element.style.width = `${value}%`;
    }

    /**
     * עדכון class של element
     */
    updateClass(element, className) {
        if (!element) return;

        // הסרת classes ישנים של temperature
        const oldClasses = element.className.match(/progress-bar-temp-\w+/g);
        if (oldClasses) {
            oldClasses.forEach(cls => element.classList.remove(cls));
        }

        // הוספת class חדש עם הקידומת הנכונה
        if (className) {
            // בדיקה אם זה progress-bar - צריך להוסיף progress-bar-temp-
            if (element.classList.contains('progress-bar')) {
                element.classList.add(`progress-bar-temp-${className}`);
            } else {
                // אחרת, הוסף את ה-class ישירות
                element.classList.add(className);
            }
        }
    }

    /**
     * שליחת ping לבדיקת חיבור
     */
    ping() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ action: "ping" }));
        }
    }
}

// יצירת instance גלובלי (אופציונלי)
window.WebSocketClient = WebSocketClient;

