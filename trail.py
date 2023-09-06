from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       _____top______
      /              \
    -<                >-following- 
      \____bottom____/
    """

    top: Trail
    bottom: Trail
    following: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return TrailSeries(self.following.store.mountain, self.following.store.following)

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Removing the mountain at the beginning of this series.
        """
        return self.following

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain in series before the current one.
        """
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        return TrailSplit(Trail(None), Trail(None), Trail(self))
    
    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSplit(Trail(None), Trail(None), self.following)))

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return Trail(TrailSplit(Trail(None), Trail(None), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""
        from personality import PersonalityDecision # Avoid circular import
        from data_structures.linked_stack import LinkedStack, Node # Use a Linked Stack because we don't know how many mountains there are and Linked variation is easier to resize
        following_splits = LinkedStack() # Store the following trails of each split. 
        current_trail = self
        # Must check if we are not dealing with a finished trail from the start
        if current_trail.store.following is not None:
            following_exists = True
        else:
            following_exists = False 
        inside_split = False
        while following_exists: # We want to end this when there is no more following, or break when walker wants to stop
            if not following_splits.is_empty():
                inside_split = True
            else:
                inside_split = False
            if type(current_trail) == Trail:
                current_trail = current_trail.store

            if type(current_trail) == TrailSplit:
                following = current_trail.following
                top = current_trail.top
                bottom = current_trail.bottom
                following_splits.push(following)
                decision = personality.select_branch(top, bottom)
                if decision == PersonalityDecision.TOP:
                    current_trail = top
                    continue
                elif decision == PersonalityDecision.BOTTOM:
                    current_trail = bottom
                    continue
                elif decision == PersonalityDecision.STOP:
                    break
            elif type(current_trail) == TrailSeries:
                personality.add_mountain(current_trail.mountain)
                if inside_split and current_trail.following.store == None:
                    current_trail = following_splits.pop()
                    continue
            elif current_trail == None:
                # skip, don't do anything, just go to following.
                if inside_split:
                    current_trail = following_splits.pop()
                    continue
                

            # How do we check whether the trail no longer has a following?
            # 1. It's a series and following is equal to None, or the following is Trail(None)
            # 2. All splits have been closed. If we reach the following of a split, we can consider it to be closed. Once all splits have been exhausted (splits is empty) and following is a series with following none, trail is over.
            if following_splits.is_empty():
                if type(current_trail) == TrailSeries:
                    if current_trail.following.store == None:
                        following_exists = False
                else:
                    if current_trail.store == None:
                        following_exists = False
            if following_exists:
                current_trail = current_trail.following
                


    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        raise NotImplementedError()

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        raise NotImplementedError()

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
