;Problems:

; Note slight inefficiency in twist-mult
; f81 and f9<2> have not been checked for accuracy.
; solver has not been implimented.


(define log1 '())

(define (clearlog) (set! log1 '()))

(define (log . comments)
   (set! log1 
         (append log1 (list comments)))
;   (display comments)
;   (newline)
)

(define (Z-p p)
  (define (elts n)
    (if (= n 0)
	'(0)
	(append (elts (- n 1)) (list n))))
 (define (self) (Z-p p))
  (lambda (command . args)
    (cond ((equal? command 'commands)
           '(commands elements * + - 0 1 simplify characteristic frobenious rank ancestry))
          ((equal? command 'elements)
	   (elts (- p 1)))
          ((equal? command 'self)
           (self))
	  ((equal? command '*)
	   (remainder (* (car args) (cadr args)) p))
	  ((equal? command '+)
	   (remainder (+ (car args) (cadr args)) p))
	  ((equal? command '-)
	   (remainder (- (car args) (cadr args)) p))
	  ((equal? command 'simplify)
	   (let ((r (remainder (car args) p)))
	     (if (< r 0)
		 (+ r p)
		 r)))
	  ((equal? command 'characteristic)
	   p)
	  ((equal? command '0)
	   0)
          ((equal? command '1)
           1)
	  ((equal? command 'frobenius)
	   (car args))
	  ((equal? command 'rank);; rank is rank over Z/p
	   1)
          ((equal? command 'ancestry)
           (list 'Z/ p))
          (else (error1))
           )))
           
(define (error1) (print "Not a valid command.  Use 'commands to view valid commands"))           

(define (all-appends lsts1 lsts2)
  (if (null? (cdr lsts1))
      (map (lambda (lst) (append (car lsts1) lst)) lsts2)
      (append
       (map (lambda (lst) (append (car lsts1) lst)) lsts2)
       (all-appends (cdr lsts1) lsts2))))

(define (poly-mult ring coeff-ring l-poly r-poly)
  (define d1 (- (length l-poly) 1))
  (define d2 (- (length r-poly) 1))
  (define num-terms (+ d1 d2 1))
  (define (one-term l r-poly shift)
     (append
            (zerolst shift (coeff-ring '0))
            (map (lambda (term)
                    (coeff-ring '* l term))
                 r-poly)))              
  (define (extra-0s lst num-terms)
    (if (>= (length lst) num-terms)
	lst
	(append (extra-0s lst (- num-terms 1)) (list (coeff-ring '0)))))
  (define (product l-poly r-poly shift)
    (if (null? (cdr l-poly))
       (extra-0s (one-term (car l-poly) r-poly shift) num-terms)
       (ring '+ 
             (extra-0s (one-term (car l-poly) r-poly shift) num-terms)
             (product (cdr l-poly) r-poly (+ shift 1)))))
  (define p (product l-poly r-poly 0))
  (log 'poly-mult l-poly r-poly (list 'have 'product p))
  p)

(define (twist-mult ring coeff-ring l-poly r-poly exp) ;let sigma be the generator of G=Z/mZ; it acts as frobenius^exp and thereby fixes F_{p^exp}.
  (define d1 (- (length l-poly) 1))
  (define d2 (- (length r-poly) 1))
  (define num-terms (+ d1 d2 1))
  (define (one-term l r-poly shift)
    (define ans
        (append 
             (zerolst shift (coeff-ring '0))
             (map (lambda (term) 
                     (coeff-ring '*
                                  l 
                                  (coeff-ring 'frobenius term (* shift exp))))
                  r-poly)))
    (log 'oneterm-data: l r-poly shift 'returns: ans)
    ans)  
  (define (extra-0s lst num-terms)
    (if (>= (length lst) num-terms)
	lst
	(append (extra-0s lst (- num-terms 1)) (list (coeff-ring '0)))))
  (define (product l-poly r-poly shift)
    (if (null? (cdr l-poly))
       (begin (log '(calling one-term) 'shift shift) (one-term (car l-poly) r-poly shift))
       (ring '+
             (extra-0s (one-term (car l-poly) r-poly shift) num-terms)
             (product (cdr l-poly) r-poly (+ shift 1)))))
  (define p (product l-poly r-poly 0))
  (log 'twist-mult l-poly r-poly (list 'have 'twistproduct p))
  p)

(define (first-n lst n)
  (if (= n 0)
      '()
      (cons (car lst) (first-n (cdr lst) (- n 1)))))

(define (last lst)
  (if (null? (cdr lst))
      (car lst)
      (last (cdr lst))))

(define (zerolst n zero)
  (if (= n 0)
      '()
      (cons zero (zerolst (- n 1) zero))))

(define (reduce-poly ring poly monic)  ;We are looking at the image of poly in ring[x]/monic(x).
  (define deg-p (- (length poly) 1))
  (define deg-i (length monic))
  (define ans
     (if (< deg-p deg-i)
      poly
      (reduce-poly 
       ring 
       (map (lambda (r1 r2) (ring '- r1 r2))
	    (first-n poly deg-p)
	    (append (zerolst (- deg-p deg-i) (ring '0))
		    (map (lambda (m) (ring '* (last poly) m)) monic)))
       monic)))
  (log 'reduce-poly 'returns ans)
   ans)

(define (repeat proc arg n)
  (if (= n 0)
      arg
      (proc (repeat proc arg (- n 1)))))

(define (extension ring monic)
  (define deg (length monic))
  (define (simplify x)
    ((extension ring monic) 'simplify x))
  (define (all-elts n) 
    (if (= n 0)
	(map (lambda (x) (list x)) (ring 'elements))
	(all-appends 
	 (map (lambda (x) (list x)) (ring 'elements))
	 (all-elts (- n 1)))))
  (define (self) (extension ring monic))
  (lambda (command . args)
    (cond  ((equal? command 'commands)
            '(commands elements * + - 0 1 simplify degree image characteristic frobenious rank ancestry))
           ((equal? command 'degree)
	   deg)
	  ((equal? command 'elements)
	   (all-elts (- deg 1)))
          ((equal? command 'self)
           (self))
          ((equal? command 'image)
           (cons (car args) (zerolst (- deg 1) (ring '0))))
	  ((equal? command '+)
	   (simplify (map (lambda (r1 r2) (ring '+ r1 r2)) (car args) (cadr args))))
	  ((equal? command '-)
	   (simplify (map (lambda (r1 r2) (ring '- r1 r2)) (car args) (cadr args))))
	  ((equal? command '*)
	   (simplify (reduce-poly
		      ring 
		      (poly-mult (self) ring (car args) (cadr args)) 
		      monic)))
	  ((equal? command '0)
	   (zerolst deg (ring '0)))
          ((equal? command '1)
           (cons (ring '1) (zerolst (- deg 1) (ring '0))))
	  ((equal? command 'simplify)
	   (map (lambda (x) (ring 'simplify x)) (car args)))
	  ((equal? command 'characteristic)
	   (ring 'characteristic))
	  ((equal? command 'frobenius)
	   (simplify 
	     (if (= (cadr args) 0)
                 (car args)
                 (begin
                    (log 'frobenius)
                    (repeat
                           (lambda (x) ((self) '* (car args) x))
                           (car args)
                           (- (* (cadr args) (ring 'characteristic)) 1))))))
     	  ((equal? command 'rank)
	   (* deg (ring 'rank)))
          ((equal? command 'ancestry)
           (list 'extension (ring 'ancestry) monic) 
                 )
          (else (error1))
	  )))
	    

(define (skew ring fixed grp-order) ;; let ring/fixed be a field ext.  we find the skew grp-ring: ring<G> for G=Z/grp-orderZ.  Only makes sense if deg(ring/fixed) divides grp-order
 (define (all-elts exp) 
    (if (= exp 0)
	(map (lambda (x) (list x)) (ring 'elements))
	(all-appends 
	 (map (lambda (x) (list x)) (ring 'elements))
	 (all-elts (- exp 1)))))
  (define (self) (skew ring fixed grp-order))
   (define sigma-relation 
     (cons (ring '- (ring '0) (ring '1)) (zerolst (- grp-order 1) (ring '0))))
   (lambda (command . args)
     (cond  ((equal? command 'commands)
             '(commands elements * + - 0 1 simplify characteristic rank ancestry))
            ((equal? command 'elements)
             (all-elts (- grp-order 1)))
            ((equal? command 'self)
            (self))
           ((equal? command 'image)
            (cons (car args) (zerolst (- grp-order 1) (ring '0)))) 
	   ((equal? command '+)
	    (map (lambda (r1 r2) (ring '+ r1 r2)) (car args) (cadr args)))
           ((equal? command '0)
            (zerolst grp-order (ring '0)))
           ((equal? command '1)
            (cons (ring '1) (zerolst (- grp-order 1) (ring '0)))) 
	   ((equal? command '-)
	    (map (lambda (r1 r2) (ring '- r1 r2)) (car args) (cadr args)))
	   ((equal? command '*)
            (reduce-poly
	     ring 
	     (twist-mult (self) ring (car args) (cadr args) (fixed 'rank))
	     sigma-relation))
	   ((equal? command 'rank)
	    (* grp-order (ring 'rank)))
           ((equal? command 'characteristic)
            (ring 'characteristic)) 
           ((equal? command 'ancestry)
            (list 'skew (ring 'ancestry) 'fixed: (fixed 'ancestry) 'order: grp-order))
	   (else (error1)))))
     
(define (all-combinations lsts)
   (cond ((null? (cdr lsts))
          (map list (car lsts)))
         ((null? (car lsts))
          '())
         (else
            (append (map (lambda (x) (cons (caar lsts) x))
                         (all-combinations (cdr lsts)))
                    (all-combinations (cons (cdar lsts) (cdr lsts)))))))
        
(define (solver ring funcs . list-of-sets)
   (define func-list
      (if (list? funcs)
         funcs
         (list funcs)))
   (define cons-append
      (if (= (length list-of-sets) 1)
         append
         cons))
   (define (all-zero? func-list args)
      (if (null? func-list)
         #t
         (and (equal?
                     (ring '0) 
                     (apply (car func-list) args))
             (all-zero? (cdr func-list) args))))
              
   (define (find-sol value-list)
;      (display (car value-list))
;      (newline)
      (cond ((null? value-list)
             '())
            ((all-zero? func-list (cons ring (car value-list)))
             (cons-append (car value-list) (find-sol (cdr value-list))))
            (else (find-sol (cdr value-list)))))
   (find-sol (all-combinations list-of-sets)))            
     
(define f3 (z-p 3))
(define f9 (extension f3 '(1 0))) ;this is (Z/3Z)[x]/x^2+1
(define f81 (extension f9 '((1 2) (0 0)))); this is F9[y]/y^2+2x+1
(define f9<2> (skew f9 f3 2))
(define f9<1> (skew f9 f3 1))

(define f2 (z-p 2))
(define f8 (extension f2 '(1 1 0)))
(define f8<3> (skew f8 f2 3))

(define xy-1 (lambda (ring x1 x2) (ring '- (ring '* x1 x2) (ring '1))))
(define x^2-x (lambda (ring x) (ring '- (ring '* x x) x)))
(define x+y-1 (lambda (ring x y) (ring '- (ring '+ x y) (ring '1))))
(define x*y (lambda (ring x y) (ring '* x y)))

(define idem (solver f9<2> x^2-x (f9<2> 'elements)))
(define dudes (solver f9<2> (list x+y-1 x*y) idem idem))

















