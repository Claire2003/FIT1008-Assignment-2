"""
Trail class. Stores information regarding type of trail, and trail operations.
"""
from __future__ import annotations
__author__ = "Haru Le"
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

    Unless stated otherwise, all methods have O(1) complexity.
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
  
    Unless stated otherwise, all methods have O(1) complexity.
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
    """
    Trail class to store trail types.
  
    Unless stated otherwise, all methods have O(1) complexity.
    """
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
        """Follow a path and add mountains according to a personality.

        :personality: Personality that indicates the branches to choose. WalkerPersonality.

        :complexity: Best O(1) Worst O(n), where n is the number of trails inside of the path.
        Best case: Lazy Personality encounters top and bottom series of equal difficulty at the start of a trail.
        Worst case: Walker goes through all trails.
        """
        from personality import PersonalityDecision # Avoid circular import
        from data_structures.linked_stack import LinkedStack # Use a Linked Stack because we don't know how many mountains there are and Linked variation is easier to resize

        following_splits = LinkedStack() # Store the following trails of each split. 
        current_trail = self
        # Must check if we are not dealing with a finished trail from the start
        if current_trail.store.following is not None:
            following_exists = True
        else:
            following_exists = False 
        # Can also be written as following_exists = current_trail.store.following is not None
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
            # 2. All splits have been closed. If we reach the following of a split, we can consider it to be closed. 
            #    Once all splits have been exhausted (splits is empty) and following is a series with following none, trail is over.
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
        """Returns a list of all mountains on the trail.
        Does this by using recursion and getting all mountains from the next sequential trail.
        :current_trail: The current trail we want to extract following mountains from. 
        :following_splits: Linked Stack that holds all following trails from splits. 
        :comp: O(n) 
        Where n is the number of mountains and branches combined in the path. 
        """
        from data_structures.linked_stack import LinkedStack
        all_mountains = []
        following_splits = LinkedStack()
        self._collect_all_mountains_aux(self.store, following_splits, all_mountains)
        return all_mountains
    
    from data_structures.linked_stack import LinkedStack
    def _collect_all_mountains_aux(self, current_trail: TrailStore, following_splits: LinkedStack, all_mountains: list[Mountain]):
        from data_structures.linked_stack import LinkedStack
        # Base case?
        # When there are no more following splits to go through and we reach the end of a series/nothing more to look at.
        if following_splits.is_empty() and current_trail is None:
            return

        if type(current_trail) is TrailSeries:
            all_mountains.append(current_trail.mountain)
            self._collect_all_mountains_aux(current_trail.following.store, following_splits, all_mountains)
        elif type(current_trail) is TrailSplit:
            following = current_trail.following.store
            top = current_trail.top.store
            bottom = current_trail.bottom.store
            following_splits.push(following)
            # Create two following splits.
            # temp_stack = LinkedStack() 
            # dupe_splits_1 = LinkedStack()
            # dupe_splits_2 = LinkedStack()
            # while not following_splits.is_empty():
            #     temp_stack.push(following_splits.pop())

            # while not temp_stack.is_empty():
            #     trail = temp_stack.pop()
            #     print(type(trail))
            #     dupe_splits_1.push(trail)
            #     dupe_splits_2.push(trail)

            # The reason why we don't maintain the splits, is because, once we have gone all the way to the end,
            # We don't want to repeatedly come out of the splits.
            # This would end up in duplicate elements. 
            # Luckily we can just leave as is. 
            self._collect_all_mountains_aux(top, following_splits, all_mountains)
            self._collect_all_mountains_aux(bottom, following_splits, all_mountains)
        elif current_trail is None:
            if not following_splits.is_empty():
                self._collect_all_mountains_aux(following_splits.pop(), following_splits, all_mountains)

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        # Try figure out why input size is so important, I suspect that it's because it might make us choose which data structure to use.
        # If we know the max size, then Stack is better.

        # Need recursive function that returns a list of possible paths (list of trails) that we could take.
        # Either while we recurse, we filter out the ones that don't fit the requirement, 
        # Or at the end, we have difficulty level's associated with each path.
        
        from data_structures.linked_stack import LinkedStack
        paths = []
        following_splits = LinkedStack()
        self._difficulty_maximum_paths_aux(max_difficulty, self.store, following_splits, [] , paths)
        return paths

    def _difficulty_maximum_paths_aux(self, max_difficulty: int, current_trail: TrailStore, following_splits: LinkedStack, current_path: list[Mountain], paths: list[list[Mountain]]):
        from data_structures.linked_stack import LinkedStack
        # Start with trying to make recursive algorithm to get all paths. 
        # How to get a single path? 
        # It's like collecting all mountains, but we want to regain the splits, and we want to add everything to a path list in the process.

        # Paths are distinct when different branches are chosen. 
        # Therefore, it can be thought that when encountering a branch, we create a new path object, with the same all prev elements in it. 
        # Then when we reach the end for both paths, we add them to paths.
        if following_splits.is_empty() and current_trail is None:
            paths += [current_path]
            return

        if type(current_trail) is TrailSeries:
            if current_trail.mountain.difficulty_level <= max_difficulty:
                current_path.append(current_trail.mountain)
                self._difficulty_maximum_paths_aux(max_difficulty, current_trail.following.store, following_splits, current_path, paths)
            else:
                return
        elif type(current_trail) is TrailSplit:
            following = current_trail.following.store
            top = current_trail.top.store
            bottom = current_trail.bottom.store
            following_splits.push(following)
            # Create two following splits.
            temp_stack = LinkedStack() 
            dupe_splits_1 = LinkedStack()
            dupe_splits_2 = LinkedStack()
            while not following_splits.is_empty():
                temp_stack.push(following_splits.pop())

            while not temp_stack.is_empty():
                trail = temp_stack.pop()
                dupe_splits_1.push(trail)
                dupe_splits_2.push(trail)

            current_path_copy = [trail for trail in current_path]
            self._difficulty_maximum_paths_aux(max_difficulty, top, dupe_splits_1, current_path, paths)
            self._difficulty_maximum_paths_aux(max_difficulty, bottom, dupe_splits_2, current_path_copy, paths)
        elif current_trail is None:
            if not following_splits.is_empty():
                self._difficulty_maximum_paths_aux(max_difficulty, following_splits.pop(), following_splits, current_path, paths)


    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
