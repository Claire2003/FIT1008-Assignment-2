"""
Trail class. Stores information regarding type of trail, and provides trail operations.
"""
from __future__ import annotations
__author__ = "Haru Le"
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality
    from data_structures.linked_stack import LinkedStack

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

        :complexity best: O(1) 
        :complexity worst: O(n)
        Where n is the length of the longest path of trails inside of the whole track.
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

        :return: all_mountains, list of mountains on the trail. 
        
        :complexity: O(_collect_all_mountains_aux())
        """
        from data_structures.linked_stack import LinkedStack
        all_mountains = []
        following_splits = LinkedStack()
        self._collect_all_mountains_aux(self.store, following_splits, all_mountains)
        return all_mountains
    
    def _collect_all_mountains_aux(self, current_trail: TrailStore, following_splits: LinkedStack, all_mountains: list[Mountain]):
        """
        Adds to a list of all mountains following the current_trail.
        Done using recursion and getting all mountains from the next sequential trail.
        :current_trail: The current trail we want to extract following mountains from. 
        :following_splits: Linked Stack that holds all following trails from splits. 
        :all_mountains: Accumulator that holds mountains we want to store.

        :complexity best: O(1) (current_trail is final trail)
        :complexity worst: O(n)
        Where n is the highest number of trails that come after current_trail.
        """
        from data_structures.linked_stack import LinkedStack
        # Base case?
        # When there are no more following splits to go through and we reach the end of a series/nothing more to look at.
        if following_splits.is_empty() and current_trail is None:
            return
        
        if type(current_trail) is TrailSeries:
            # Add to accum if current_trail is a series. As it must have a mountain. 
            all_mountains.append(current_trail.mountain)
            # Since it is a series, we analyse the next trail in the series.
            self._collect_all_mountains_aux(current_trail.following.store, following_splits, all_mountains)
        elif type(current_trail) is TrailSplit:
            # When a split occurs, we want to store following for after we have gone through the split
            # The way it is implemented here, we will go through the top branch until we have reached the end.
            # After that, we go through the bottom branch just to make sure we captured everything, 
            # However we don't go to the end, as that would result in repeating mountains
            following = current_trail.following.store
            top = current_trail.top.store
            bottom = current_trail.bottom.store
            following_splits.push(following)
            self._collect_all_mountains_aux(top, following_splits, all_mountains)
            self._collect_all_mountains_aux(bottom, following_splits, all_mountains)
        elif current_trail is None:
            # Because following splits is not empty and current trail is not None, 
            # It means that we must have reached the end of a split, but not the whole trail.
            # Therefore, we want to continue, and keep collecting mountains from the following of the prior split we went into. 
            if not following_splits.is_empty():
                self._collect_all_mountains_aux(following_splits.pop(), following_splits, all_mountains)

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        """
        Given an integer max_difficulty, calculate all paths through the trail such that the maximum difficulty of all mountains in the path does not exceed maximum_difficulty.
        The return value of this should be a list containing lists, containing the Mountains on each path, in order taken in the path.

        Paths are considered distinct if any branch decision chosen is different, even if the mountains traversed would be the same.

        :return: paths list[list[Mountain]] object of all paths that satisfy the requirement.

        :complexity: O(_difficulty_maximum_paths_aux())
        """
        from data_structures.linked_stack import LinkedStack
        paths = []
        following_splits = LinkedStack()
        # Start from the start, and ensure current path is nothing before accumulating
        self._difficulty_maximum_paths_aux(max_difficulty, self.store, following_splits, [] , paths)
        return paths

    def _difficulty_maximum_paths_aux(self, max_difficulty: int, current_trail: TrailStore, following_splits: LinkedStack, current_path: list[Mountain], paths: list[list[Mountain]]):
        """
        Adds to a list of all paths that satisfy the max_difficulty condition.
        Done using recursion and getting paths from the next sequential trail, and checking the condition.
        :max_difficulty: Integer that represents the maximum difficulty any mountain in the paths can be. 
        :current_trail: The current trail we want to extract following paths from. 
        :following_splits: Linked Stack that holds all following trails from splits. 
        :current_path: List of mountains that represents a path.
        :paths: List of list of mountains that holds all paths that satisfy the condition.

        :complexity best: O(1)
        :complexity worst: O(n*m)
        Where n is the total number of trails that come after current_trail.
        Best case: current_trail is final trail
        Worst case: current_trail is the start trail and you go through as many paths as there are branches. 
        No path is invalid, so every path is considered. 
        Visiting each trail multiple times. All the following trails get done twice. 
        However if it not n^2, or other, rather just a multiple of the amount of trails in the whole track.
        m comes from copying prior mountains when splitting paths.
        Where m is the number of mountains in the current path. 
        """
        from data_structures.linked_stack import LinkedStack
        # It's like collecting all mountains, but we want to regain the splits, and we want to add everything to a path list in the process.
        # Paths are distinct when different branches are chosen. 
        # Therefore, it can be thought that when encountering a branch, we create a new path object, with the same all prev elements in it. 
        # Then when we reach the end for both paths, we add them to paths.
        if following_splits.is_empty() and current_trail is None:
            # Add to paths list, as we reached final. 
            paths += [current_path]
            return

        if type(current_trail) is TrailSeries:
            if current_trail.mountain.difficulty_level <= max_difficulty:
                # Append mountains along the way.
                current_path.append(current_trail.mountain)
                self._difficulty_maximum_paths_aux(max_difficulty, current_trail.following.store, following_splits, current_path, paths)
            else:
                # Reduces complexity, don't add to paths, and stop recursing from here. For this branch.
                return
        elif type(current_trail) is TrailSplit:
            following = current_trail.following.store
            top = current_trail.top.store
            bottom = current_trail.bottom.store
            following_splits.push(following)
            # Create two following splits. To not lose the following split info when taking paths from top and bottom of split.
            temp_stack = LinkedStack() 
            dupe_splits_1 = LinkedStack()
            dupe_splits_2 = LinkedStack()
            # Copying stacks can be thought of as constant as max branches are 5, and thus only 5 following branches possible.
            while not following_splits.is_empty():
                temp_stack.push(following_splits.pop())

            while not temp_stack.is_empty():
                trail = temp_stack.pop()
                dupe_splits_1.push(trail)
                dupe_splits_2.push(trail)
            # Deep copy current path, as method relies on side effects.
            # O(m) where m is the number of mountains in current_path
            current_path_copy = [mtn for mtn in current_path]
            # Create two new paths
            self._difficulty_maximum_paths_aux(max_difficulty, top, dupe_splits_1, current_path, paths)
            self._difficulty_maximum_paths_aux(max_difficulty, bottom, dupe_splits_2, current_path_copy, paths)
        elif current_trail is None:
            if not following_splits.is_empty():
                self._difficulty_maximum_paths_aux(max_difficulty, following_splits.pop(), following_splits, current_path, paths)


    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
