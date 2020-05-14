;;;; nbt-explorer.asd

(asdf:defsystem #:nbt-explorer
  :description "Application for exploring Named Binary Tag files."
  :author "Izak Halseide <halseide.izak@gmail.com>"
  :license  "MIT License"
  :version "0.0.1"
  :serial t
  :depends-on (#:binary-data)
  :components ((:file "packages")
               (:file "nbt-data")
               (:file "nbt-explorer")))
