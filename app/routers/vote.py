from fastapi import FastAPI ,Response ,status ,HTTPException, Depends ,APIRouter, Depends
import models, schemas, utils, oauth2, database
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/vote",
    tags= ["Vote"]
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    posts = db.query(models.Pomst).filter(models.Pomst.id == vote.post_id).first()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {vote.post_id} doesn't exist")

    vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.user_id == current_user.id)
    found_vote = vote_query.first()
    #vote 1 denotes liked a post while vote 0 denotes you've unliked a post and deleted from database
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted on {vote.post_id}")
        new_vote = models.Votes(post_id= vote.post_id, user_id= current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"Successfully added vote"}
    else:

        if not found_vote:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Vote doesn't exist")

        vote_query.delete(synchronize_session= False)
        db.commit()
        return {"message":"successfully deleted"}

