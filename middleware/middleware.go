package main

import (
  "crypto/md5"
  "flag"
  "fmt"
  "log"
  "net/http"
  "strconv"
  "io"
  "net/http/httptest"
  "strings"
  "bytes"
)

const (
  crlf       = "\r\n"
  colonspace = ": "
  semicolon = "; "
)

func ChecksumMiddleware(h http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    // your code goes here ...
    rec := httptest.NewRecorder()
    // passing a ResponseRecorder instead of the original ResponseWriter
    h.ServeHTTP(rec, r)
    // after this finishes, we have the response recorded
    // and can modify it before copying it to the original ResponseWriter
    code := strconv.Itoa(rec.Code)
    h_s := rec.Header()
    var buffer1 bytes.Buffer
    var buffer2 bytes.Buffer
    header_names := []string{"Content-Type", "Date", "Last-Modified", "Server"}
    for _, item := range header_names {
      buffer1.WriteString(strings.Join([]string{
        item,
        colonspace,
        h_s.Get(item),
        crlf,
    }, ""))
  }
    for _, x := range h_s.Get("X-Checksum-Headers") {
      buffer2.WriteString(strings.Join([]string{
      string(x),
    }, semicolon))
  }
    b := rec.Body.Bytes()
    body := string(b[:len(b)])
    canonical := strings.Join([]string{
      code,
      crlf,
      buffer1.String(),
      buffer2.String(),
      crlf + crlf,
      body,
  }, "")
    c := md5.New()
    io.WriteString(c, canonical)
    //sum := c.Sum(nil)
    sum2 := md5.Sum([]byte(canonical))
    //sumString := string(sum[:])
    sum2String := string(sum2[:])
    // we copy the original headers first
    for k, v := range rec.Header() {
        w.Header()[k] = v
    }
    // and set an additional one
    w.Header().Set("X-Checksum", sum2String)
    // only then the status code, as this call writes out the headers
    w.WriteHeader(418)
    // finally, write out our data
    // w.Write(data)
    // then write out the original body
    w.Write(rec.Body.Bytes())
  })
}

// Do not change this function.
func main() {
  var listenAddr = flag.String("http", "localhost:8080", "address to listen on for HTTP")
  flag.Parse()

  http.Handle("/", ChecksumMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("X-Foo", "bar")
    w.Header().Set("Content-Type", "text/plain")
    w.Header().Set("Date", "Sun, 08 May 2016 14:04:53 GMT")
    msg := "Curiosity is insubordination in its purest form.\n"
    w.Header().Set("Content-Length", strconv.Itoa(len(msg)))
    fmt.Fprintf(w, msg)
  })))

  log.Fatal(http.ListenAndServe(*listenAddr, nil))
}
