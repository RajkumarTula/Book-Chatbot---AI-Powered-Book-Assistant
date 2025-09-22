import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FaSearch, 
  FaStar, 
  FaTrophy, 
  FaCalendar, 
  FaDollarSign, 
  FaStarHalfAlt,
  FaBook
} from 'react-icons/fa';

const SidebarContainer = styled.div`
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
`;

const Section = styled.div`
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h3`
  color: #495057;
  margin-bottom: 1rem;
  font-weight: 600;
`;

const QuickActions = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const QuickActionButton = styled(motion.button)`
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: #495057;
  transition: all 0.3s ease;
  text-align: left;
  
  &:hover {
    background: #667eea;
    color: white;
    transform: translateX(5px);
  }
`;

const IconWrapper = styled.div`
  width: 20px;
  text-align: center;
  flex-shrink: 0;
`;

const FeaturedBooks = styled.div`
  margin-top: 2rem;
`;

const BookCards = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const BookCard = styled(motion.div)`
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
`;

const BookTitle = styled.h4`
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: #333;
  line-height: 1.3;
`;

const BookAuthor = styled.p`
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.25rem;
`;

const BookDate = styled.p`
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.5rem;
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
`;

const Stars = styled.div`
  color: #ffd700;
  display: flex;
  gap: 0.1rem;
`;

const Star = styled.span`
  font-size: 0.8rem;
`;

const RatingCount = styled.span`
  font-size: 0.8rem;
  color: #666;
  margin-left: 0.25rem;
`;

const quickActions = [
  { id: 'search', icon: FaSearch, label: 'Search Books' },
  { id: 'recommend', icon: FaStar, label: 'Get Recommendations' },
  { id: 'bestsellers', icon: FaTrophy, label: 'Bestsellers' },
  { id: 'new-releases', icon: FaCalendar, label: 'New Releases' },
  { id: 'price', icon: FaDollarSign, label: 'Check Price' },
  { id: 'rating', icon: FaStarHalfAlt, label: 'Check Rating' },
];

function Sidebar({ onQuickAction, featuredBooks, onBookClick }) {
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <Stars>
        {[...Array(fullStars)].map((_, i) => (
          <Star key={i}><FaStar /></Star>
        ))}
        {hasHalfStar && <Star><FaStarHalfAlt /></Star>}
        {[...Array(emptyStars)].map((_, i) => (
          <Star key={i + fullStars + (hasHalfStar ? 1 : 0)}>
            <FaBook style={{ color: '#ddd' }} />
          </Star>
        ))}
      </Stars>
    );
  };

  return (
    <SidebarContainer>
      <Section>
        <SectionTitle>Quick Actions</SectionTitle>
        <QuickActions>
          {quickActions.map((action) => (
            <QuickActionButton
              key={action.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onQuickAction(action.id)}
            >
              <IconWrapper>
                <action.icon />
              </IconWrapper>
              {action.label}
            </QuickActionButton>
          ))}
        </QuickActions>
      </Section>

      <FeaturedBooks>
        <SectionTitle>Featured Books</SectionTitle>
        <BookCards>
          {featuredBooks.map((book, index) => (
            <BookCard
              key={book.title || index}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onBookClick(book.title)}
            >
              <BookTitle>{book.title}</BookTitle>
              <BookAuthor>by {book.authors?.join(', ') || 'Unknown Author'}</BookAuthor>
              <BookDate>{book.published_date}</BookDate>
              {book.average_rating && (
                <RatingContainer>
                  {renderStars(book.average_rating)}
                  <RatingCount>({book.ratings_count} ratings)</RatingCount>
                </RatingContainer>
              )}
            </BookCard>
          ))}
        </BookCards>
      </FeaturedBooks>
    </SidebarContainer>
  );
}

export default Sidebar;



