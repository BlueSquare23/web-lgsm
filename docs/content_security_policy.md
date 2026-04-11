## 🔐 Security Headers Overview

This application uses HTTP security headers to reduce attack surface while maintaining compatibility with a dashboard-style frontend using libraries such as Bootstrap, CodeMirror, and xterm.js.

---

## 🧱 X-Content-Type-Options

```http
X-Content-Type-Options: nosniff
```

Prevents browsers from guessing the MIME type of files.

* Stops “MIME sniffing” attacks
* Ensures scripts and styles are only executed if explicitly declared

---

## 🧭 X-Frame-Options

```http
X-Frame-Options: SAMEORIGIN
```

Prevents clickjacking by restricting iframe embedding.

* Only pages from the same domain can embed this site
* Blocks external sites from framing the application

---

## 🛡 Content Security Policy (CSP)

CSP restricts what resources the browser is allowed to load and execute.

```http
Content-Security-Policy: ...
```

### 🔹 default-src 'self'

Sets the default rule to only allow resources from the same origin unless explicitly permitted.

---

### 🔹 script-src

```text
'self' 'unsafe-inline' 'unsafe-eval'
https://ajax.googleapis.com
https://cdn.jsdelivr.net
https://cdnjs.cloudflare.com
```

Allows JavaScript from:

* Local application files (`'self'`)
* Inline scripts (required for Flask templates)
* Dynamic JS execution (required by some libraries)
* External CDNs used by frontend dependencies

Used for:

* Bootstrap dependencies
* jQuery
* CodeMirror
* xterm.js functionality

---

### 🔹 style-src

```text
'self' 'unsafe-inline'
https://cdn.jsdelivr.net
https://cdnjs.cloudflare.com
```

Allows CSS from:

* Local stylesheets
* Inline styles (required by some UI libraries)
* Bootstrap and CodeMirror CDN styles

---

### 🔹 img-src

```text
'self' data: blob: https:
```

Allows images from:

* Local server
* Inline/base64 images (`data:`)
* Dynamically generated images (`blob:`)
* External HTTPS sources

---

### 🔹 font-src

```text
'self'
https://cdn.jsdelivr.net
https://cdnjs.cloudflare.com
```

Allows fonts required by:

* Bootstrap Icons
* External UI libraries

---

### 🔹 worker-src

```text
'self' blob:
```

Enables Web Workers used by:

* xterm.js for terminal rendering and performance isolation

---

### 🔹 connect-src

```text
'self' ws: wss: https:
```

Allows network connections for:

* REST API calls
* WebSocket connections (required for terminal backends)
* Secure external HTTPS APIs

---

### 🔹 frame-ancestors

```text
'self'
```

Prevents other websites from embedding this application in iframes.

* Mitigates clickjacking attacks
* Replaces legacy reliance on X-Frame-Options

---

## 🔑 Referrer Policy

```http
Referrer-Policy: strict-origin-when-cross-origin
```

Controls how much referrer information is sent when navigating away.

* Sends full URL only within same origin
* Sends only origin (not full path) to external sites

---

## 🔒 HTTP Strict Transport Security (HSTS)

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Enforces HTTPS usage for one year.

* Prevents downgrade attacks
* Ensures all subdomains use HTTPS
* Improves transport security against MITM attacks

---

# 🧠 Final assessment

### Security level: 🟢 Medium-High (practical production)

We are:

* Well protected against clickjacking
* Protected against MIME attacks
* Hardened against many XSS vectors
* Enforcing HTTPS consistently

