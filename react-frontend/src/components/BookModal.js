import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaTimes, FaStar, FaStarHalfAlt, FaBook, FaExternalLinkAlt } from 'react-icons/fa';

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.div`
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
`;

const ModalTitle = styled.h3`
  margin: 0;
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
`;

const CloseButton = styled(motion.button)`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  
  &:hover {
    background: #f8f9fa;
    color: #333;
  }
`;

const ModalBody = styled.div`
  padding: 2rem;
`;

const BookDetails = styled.div`
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
`;

const BookCover = styled.div`
  width: 200px;
  height: 280px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: #ccc;
  flex-shrink: 0;
  overflow: hidden;
  
  @media (max-width: 768px) {
    width: 150px;
    height: 200px;
    align-self: center;
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const BookInfo = styled.div`
  flex: 1;
`;

const BookTitle = styled.h2`
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.8rem;
  line-height: 1.3;
`;

const InfoRow = styled.p`
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  
  strong {
    color: #333;
    font-weight: 600;
  }
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem 0;
`;

const StarRating = styled.div`
  display: flex;
  gap: 0.1rem;
  align-items: center;
`;

const Star = styled.span`
  color: #ffd700;
  font-size: 1rem;
  
  &.empty {
    color: #ddd;
  }
`;

const PriceContainer = styled.div`
  font-size: 1.2rem;
  font-weight: 600;
  color: #28a745;
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  display: inline-block;
`;

const Description = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.2rem;
  }
  
  p {
    color: #666;
    line-height: 1.6;
    margin-bottom: 1rem;
  }
`;

const PriceInfo = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.2rem;
  }
`;

const PriceCard = styled.div`
  border: 1px solid #e9ecef;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  
  h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
    font-size: 1.1rem;
  }
  
  p {
    margin: 0.25rem 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    margin-top: 0.5rem;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const Reviews = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.2rem;
  }
`;

const ReviewCard = styled.div`
  border: 1px solid #e9ecef;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  
  .review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .reviewer-name {
    font-weight: 600;
    color: #333;
  }
  
  .review-text {
    font-size: 0.9rem;
    color: #666;
    line-height: 1.5;
    margin-bottom: 0.5rem;
  }
  
  .review-meta {
    font-size: 0.8rem;
    color: #999;
  }
`;

function BookModal({ book, onClose }) {
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <StarRating>
        {[...Array(fullStars)].map((_, i) => (
          <Star key={i}><FaStar /></Star>
        ))}
        {hasHalfStar && <Star><FaStarHalfAlt /></Star>}
        {[...Array(emptyStars)].map((_, i) => (
          <Star key={i + fullStars + (hasHalfStar ? 1 : 0)} className="empty">
            <FaBook />
          </Star>
        ))}
      </StarRating>
    );
  };

  if (!book) return null;

  return (
    <ModalOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <ModalContent
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <ModalHeader>
          <ModalTitle>{book.title}</ModalTitle>
          <CloseButton
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClose}
          >
            <FaTimes />
          </CloseButton>
        </ModalHeader>

        <ModalBody>
          <BookDetails>
            <BookCover>
              {book.thumbnail_url ? (
                <img src={book.thumbnail_url} alt={book.title} />
              ) : (
                <FaBook />
              )}
            </BookCover>
            
            <BookInfo>
              <BookTitle>{book.title}</BookTitle>
              
              <InfoRow>
                <strong>Authors:</strong> {book.authors?.join(', ') || 'Unknown'}
              </InfoRow>
              
              <InfoRow>
                <strong>Publisher:</strong> {book.publisher || 'Unknown'}
              </InfoRow>
              
              <InfoRow>
                <strong>Published:</strong> {book.published_date || 'Unknown'}
              </InfoRow>
              
              <InfoRow>
                <strong>Pages:</strong> {book.page_count || 'N/A'}
              </InfoRow>
              
              <InfoRow>
                <strong>Language:</strong> {book.language || 'Unknown'}
              </InfoRow>
              
              <InfoRow>
                <strong>ISBN-10:</strong> {book.isbn_10 || 'N/A'}
              </InfoRow>
              
              <InfoRow>
                <strong>ISBN-13:</strong> {book.isbn_13 || 'N/A'}
              </InfoRow>
              
              {book.average_rating && (
                <RatingContainer>
                  <strong>Rating:</strong>
                  {renderStars(book.average_rating)}
                  <span>({book.ratings_count} ratings)</span>
                </RatingContainer>
              )}
              
              {book.price && (
                <PriceContainer>
                  Price: ${book.price} {book.currency}
                </PriceContainer>
              )}
              
              <InfoRow>
                <strong>Availability:</strong> {book.availability || 'Unknown'}
              </InfoRow>
            </BookInfo>
          </BookDetails>

          {book.description && (
            <Description>
              <h3>Description</h3>
              <p>{book.description}</p>
            </Description>
          )}

          {book.price_info && book.price_info.length > 0 && (
            <PriceInfo>
              <h3>Price Information</h3>
              {book.price_info.map((price, index) => (
                <PriceCard key={index}>
                  <h4>{price.store_name}</h4>
                  <p><strong>Price:</strong> ${price.price} {price.currency}</p>
                  <p><strong>Availability:</strong> {price.availability}</p>
                  <p><strong>Shipping:</strong> {price.shipping_info}</p>
                  {price.url && (
                    <a href={price.url} target="_blank" rel="noopener noreferrer">
                      View on {price.store_name} <FaExternalLinkAlt />
                    </a>
                  )}
                </PriceCard>
              ))}
            </PriceInfo>
          )}

          {book.reviews && book.reviews.length > 0 && (
            <Reviews>
              <h3>Reviews</h3>
              {book.reviews.slice(0, 3).map((review, index) => (
                <ReviewCard key={index}>
                  <div className="review-header">
                    <span className="reviewer-name">{review.reviewer_name}</span>
                    {renderStars(review.rating)}
                  </div>
                  <div className="review-text">
                    {review.review_text.substring(0, 200)}...
                  </div>
                  <div className="review-meta">
                    {review.review_date} - {review.source}
                  </div>
                </ReviewCard>
              ))}
            </Reviews>
          )}
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
}

export default BookModal;



